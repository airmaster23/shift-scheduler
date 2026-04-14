from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import sqlite3
import os
from datetime import datetime, timedelta
import calendar

app = Flask(__name__)
app.secret_key = 'shift-scheduler-secret-key-2024'
DB_PATH = os.path.join(os.path.dirname(__file__), 'shifts.db')

ADMIN_PASSWORD = 'admin123'

# シフトパターン定義
SHIFT_PATTERNS = [
    {'id': 'early', 'name': '早番', 'start': '06:00', 'end': '14:00', 'color': '#4CAF50'},
    {'id': 'day', 'name': '日勤', 'start': '09:00', 'end': '17:00', 'color': '#2196F3'},
    {'id': 'late', 'name': '遅番', 'start': '14:00', 'end': '22:00', 'color': '#FF9800'},
    {'id': 'night', 'name': '夜勤', 'start': '22:00', 'end': '06:00', 'color': '#9C27B0'},
    {'id': 'short_am', 'name': '午前', 'start': '09:00', 'end': '13:00', 'color': '#00BCD4'},
    {'id': 'short_pm', 'name': '午後', 'start': '13:00', 'end': '17:00', 'color': '#E91E63'},
    {'id': 'custom', 'name': 'カスタム', 'start': '', 'end': '', 'color': '#607D8B'},
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS shift_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            work_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            pattern_id TEXT DEFAULT 'custom',
            note TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            UNIQUE(employee_id, work_date)
        );
        CREATE TABLE IF NOT EXISTS confirmed_shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            work_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            confirmed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            UNIQUE(employee_id, work_date)
        );
        CREATE TABLE IF NOT EXISTS staffing_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week INTEGER NOT NULL,
            required_count INTEGER NOT NULL DEFAULT 2,
            UNIQUE(day_of_week)
        );
    ''')
    # デフォルトの必要人数を設定
    for dow in range(7):
        conn.execute(
            'INSERT OR IGNORE INTO staffing_requirements (day_of_week, required_count) VALUES (?, ?)',
            (dow, 2)
        )
    conn.commit()
    conn.close()


init_db()


def get_month_data(year, month):
    """月のカレンダーデータを生成"""
    cal = calendar.Calendar(firstweekday=0)  # 月曜始まり
    weeks = cal.monthdayscalendar(year, month)
    return weeks


@app.route('/')
def index():
    return render_template('index.html')


# --- 従業員 ---

@app.route('/employee', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            return render_template('employee_login.html', error='名前を入力してください')
        conn = get_db()
        emp = conn.execute('SELECT * FROM employees WHERE name = ?', (name,)).fetchone()
        if not emp:
            conn.execute('INSERT INTO employees (name) VALUES (?)', (name,))
            conn.commit()
            emp = conn.execute('SELECT * FROM employees WHERE name = ?', (name,)).fetchone()
        conn.close()
        session['employee_id'] = emp['id']
        session['employee_name'] = emp['name']
        return redirect(url_for('employee_dashboard'))
    return render_template('employee_login.html')


@app.route('/employee/dashboard')
@app.route('/employee/dashboard/<int:year>/<int:month>')
def employee_dashboard(year=None, month=None):
    if 'employee_id' not in session:
        return redirect(url_for('employee_login'))

    today = datetime.now()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    weeks = get_month_data(year, month)

    # 前月・次月
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    conn = get_db()
    # この月のシフト希望
    month_str = f"{year}-{month:02d}"
    requests_list = conn.execute(
        "SELECT * FROM shift_requests WHERE employee_id = ? AND work_date LIKE ?",
        (session['employee_id'], f"{month_str}%")
    ).fetchall()
    # この月の確定シフト
    confirmed = conn.execute(
        "SELECT * FROM confirmed_shifts WHERE employee_id = ? AND work_date LIKE ?",
        (session['employee_id'], f"{month_str}%")
    ).fetchall()
    conn.close()

    # 日付ごとのデータマップ
    request_map = {r['work_date']: dict(r) for r in requests_list}
    confirmed_map = {c['work_date']: dict(c) for c in confirmed}

    today_str = today.strftime('%Y-%m-%d')

    return render_template('employee_dashboard.html',
                           name=session['employee_name'],
                           year=year, month=month,
                           weeks=weeks,
                           prev_year=prev_year, prev_month=prev_month,
                           next_year=next_year, next_month=next_month,
                           request_map=request_map,
                           confirmed_map=confirmed_map,
                           today_str=today_str,
                           today_day=today.day if year == today.year and month == today.month else -1,
                           patterns=SHIFT_PATTERNS)


@app.route('/employee/submit', methods=['POST'])
def submit_shift():
    if 'employee_id' not in session:
        return jsonify({'error': 'ログインしてください'}), 401
    data = request.get_json() if request.is_json else request.form
    work_date = data.get('work_date') or data['work_date']
    start_time = data.get('start_time') or data['start_time']
    end_time = data.get('end_time') or data['end_time']
    pattern_id = data.get('pattern_id', 'custom')
    note = data.get('note', '')

    conn = get_db()
    conn.execute(
        'INSERT OR REPLACE INTO shift_requests (employee_id, work_date, start_time, end_time, pattern_id, note) VALUES (?, ?, ?, ?, ?, ?)',
        (session['employee_id'], work_date, start_time, end_time, pattern_id, note)
    )
    conn.commit()
    conn.close()

    if request.is_json:
        return jsonify({'success': True})
    return redirect(url_for('employee_dashboard'))


@app.route('/employee/delete', methods=['POST'])
def delete_shift_request():
    if 'employee_id' not in session:
        return jsonify({'error': 'ログインしてください'}), 401
    data = request.get_json() if request.is_json else request.form
    work_date = data.get('work_date') or data['work_date']
    conn = get_db()
    conn.execute('DELETE FROM shift_requests WHERE employee_id = ? AND work_date = ?',
                 (session['employee_id'], work_date))
    conn.commit()
    conn.close()
    if request.is_json:
        return jsonify({'success': True})
    return redirect(url_for('employee_dashboard'))


@app.route('/employee/logout')
def employee_logout():
    session.pop('employee_id', None)
    session.pop('employee_name', None)
    return redirect(url_for('index'))


# --- 管理者 ---

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html', error='パスワードが違います')
    return render_template('admin_login.html')


@app.route('/admin/dashboard')
@app.route('/admin/dashboard/<int:year>/<int:month>')
def admin_dashboard(year=None, month=None):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    today = datetime.now()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    weeks = get_month_data(year, month)
    month_str = f"{year}-{month:02d}"

    # 前月・次月
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    # 月の日数
    _, days_in_month = calendar.monthrange(year, month)

    conn = get_db()
    employees = conn.execute('SELECT * FROM employees ORDER BY name').fetchall()
    requests_list = conn.execute('''
        SELECT sr.*, e.name as employee_name
        FROM shift_requests sr JOIN employees e ON sr.employee_id = e.id
        WHERE sr.work_date LIKE ?
        ORDER BY e.name
    ''', (f"{month_str}%",)).fetchall()
    confirmed_list = conn.execute('''
        SELECT cs.*, e.name as employee_name
        FROM confirmed_shifts cs JOIN employees e ON cs.employee_id = e.id
        WHERE cs.work_date LIKE ?
        ORDER BY e.name
    ''', (f"{month_str}%",)).fetchall()
    requirements = conn.execute('SELECT * FROM staffing_requirements').fetchall()
    conn.close()

    # 必要人数マップ
    req_map = {r['day_of_week']: r['required_count'] for r in requirements}

    # 従業員ごとの日付マップ
    emp_requests = {}
    emp_confirmed = {}
    for r in requests_list:
        key = (r['employee_id'], r['work_date'])
        emp_requests[key] = dict(r)
    for c in confirmed_list:
        key = (c['employee_id'], c['work_date'])
        emp_confirmed[key] = dict(c)

    # 日付ごとの確定人数
    daily_confirmed_count = {}
    for c in confirmed_list:
        d = c['work_date']
        daily_confirmed_count[d] = daily_confirmed_count.get(d, 0) + 1

    # 日付ごとの申請人数
    daily_request_count = {}
    for r in requests_list:
        d = r['work_date']
        daily_request_count[d] = daily_request_count.get(d, 0) + 1

    today_str = today.strftime('%Y-%m-%d')

    return render_template('admin_dashboard.html',
                           year=year, month=month,
                           weeks=weeks,
                           days_in_month=days_in_month,
                           prev_year=prev_year, prev_month=prev_month,
                           next_year=next_year, next_month=next_month,
                           employees=employees,
                           emp_requests=emp_requests,
                           emp_confirmed=emp_confirmed,
                           daily_confirmed_count=daily_confirmed_count,
                           daily_request_count=daily_request_count,
                           req_map=req_map,
                           today_str=today_str,
                           patterns=SHIFT_PATTERNS)


@app.route('/admin/confirm', methods=['POST'])
def confirm_shift():
    if not session.get('is_admin'):
        return jsonify({'error': '権限がありません'}), 403
    data = request.get_json() if request.is_json else request.form
    employee_id = data.get('employee_id') or data['employee_id']
    work_date = data.get('work_date') or data['work_date']
    start_time = data.get('start_time') or data['start_time']
    end_time = data.get('end_time') or data['end_time']
    conn = get_db()
    conn.execute(
        'INSERT OR REPLACE INTO confirmed_shifts (employee_id, work_date, start_time, end_time) VALUES (?, ?, ?, ?)',
        (employee_id, work_date, start_time, end_time)
    )
    conn.commit()
    conn.close()
    if request.is_json:
        return jsonify({'success': True})
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/confirm_all', methods=['POST'])
def confirm_all():
    """選択日の全申請を一括確定"""
    if not session.get('is_admin'):
        return jsonify({'error': '権限がありません'}), 403
    data = request.get_json()
    work_date = data['work_date']
    conn = get_db()
    requests_list = conn.execute(
        'SELECT * FROM shift_requests WHERE work_date = ?', (work_date,)
    ).fetchall()
    for r in requests_list:
        conn.execute(
            'INSERT OR REPLACE INTO confirmed_shifts (employee_id, work_date, start_time, end_time) VALUES (?, ?, ?, ?)',
            (r['employee_id'], r['work_date'], r['start_time'], r['end_time'])
        )
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'count': len(requests_list)})


@app.route('/admin/delete_confirmed', methods=['POST'])
def delete_confirmed():
    if not session.get('is_admin'):
        return jsonify({'error': '権限がありません'}), 403
    data = request.get_json() if request.is_json else request.form
    employee_id = data.get('employee_id') or data['employee_id']
    work_date = data.get('work_date') or data['work_date']
    conn = get_db()
    conn.execute('DELETE FROM confirmed_shifts WHERE employee_id = ? AND work_date = ?',
                 (employee_id, work_date))
    conn.commit()
    conn.close()
    if request.is_json:
        return jsonify({'success': True})
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=8080)
