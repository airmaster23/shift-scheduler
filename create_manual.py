"""シフト管理システム 操作マニュアル PDF生成スクリプト"""
from fpdf import FPDF
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'シフト管理システム_操作マニュアル.pdf')


class ManualPDF(FPDF):
    def __init__(self):
        super().__init__()
        # 日本語フォント
        font_path = self.find_font()
        if font_path:
            self.add_font('JP', '', font_path, uni=True)
            self.add_font('JP', 'B', font_path, uni=True)
            self.font_name = 'JP'
        else:
            self.font_name = 'Helvetica'

    def find_font(self):
        candidates = [
            'C:/Windows/Fonts/meiryo.ttc',
            'C:/Windows/Fonts/msgothic.ttc',
            'C:/Windows/Fonts/YuGothM.ttc',
            'C:/Windows/Fonts/msmincho.ttc',
        ]
        for f in candidates:
            if os.path.exists(f):
                return f
        return None

    def header(self):
        if self.page_no() > 1:
            self.set_font(self.font_name, '', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 8, 'シフト管理システム 操作マニュアル', align='R')
            self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_name, '', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'{self.page_no()}', align='C')

    def title_page(self):
        self.add_page()
        self.ln(60)
        # タイトル
        self.set_font(self.font_name, 'B', 28)
        self.set_text_color(74, 144, 217)
        self.cell(0, 16, 'シフト管理システム', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(4)
        self.set_font(self.font_name, '', 16)
        self.set_text_color(100, 100, 100)
        self.cell(0, 12, '操作マニュアル', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(20)
        # 区切り線
        self.set_draw_color(74, 144, 217)
        self.set_line_width(0.8)
        self.line(70, self.get_y(), 140, self.get_y())
        self.ln(20)
        # 情報
        self.set_font(self.font_name, '', 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, '提供: RH Technology', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(60)
        self.set_font(self.font_name, '', 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, '本マニュアルはシフト管理システムの基本操作をご案内します。', align='C', new_x='LMARGIN', new_y='NEXT')

    def section_title(self, num, title):
        self.ln(6)
        self.set_font(self.font_name, 'B', 16)
        self.set_text_color(74, 144, 217)
        self.cell(0, 12, f'{num}. {title}', new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(74, 144, 217)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), 200 - self.r_margin, self.get_y())
        self.ln(6)

    def sub_title(self, title):
        self.ln(3)
        self.set_font(self.font_name, 'B', 12)
        self.set_text_color(55, 65, 81)
        self.cell(0, 9, title, new_x='LMARGIN', new_y='NEXT')
        self.ln(2)

    def body_text(self, text):
        self.set_font(self.font_name, '', 10)
        self.set_text_color(55, 65, 81)
        self.multi_cell(0, 7, text)
        self.ln(2)

    def step(self, num, text):
        self.set_font(self.font_name, 'B', 10)
        self.set_text_color(74, 144, 217)
        x = self.get_x()
        self.cell(8, 7, f'{num}', new_x='END')
        self.set_font(self.font_name, '', 10)
        self.set_text_color(55, 65, 81)
        self.multi_cell(0, 7, f'  {text}')
        self.ln(1)

    def bullet(self, text):
        self.set_font(self.font_name, '', 10)
        self.set_text_color(55, 65, 81)
        x = self.get_x()
        self.cell(6, 7, '・', new_x='END')
        self.multi_cell(0, 7, text)
        self.ln(1)

    def info_box(self, title, text):
        self.ln(2)
        self.set_fill_color(232, 240, 254)
        self.set_draw_color(74, 144, 217)
        y_start = self.get_y()
        self.set_font(self.font_name, 'B', 10)
        self.set_text_color(74, 144, 217)
        self.cell(0, 8, f'  {title}', fill=True, new_x='LMARGIN', new_y='NEXT')
        self.set_font(self.font_name, '', 9)
        self.set_text_color(55, 65, 81)
        self.multi_cell(0, 6, f'  {text}', fill=True)
        self.ln(4)

    def warning_box(self, text):
        self.ln(2)
        self.set_fill_color(255, 244, 229)
        self.set_font(self.font_name, '', 9)
        self.set_text_color(184, 115, 10)
        self.multi_cell(0, 6, f'  ※ {text}', fill=True)
        self.ln(4)


def create_manual():
    pdf = ManualPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ===== 表紙 =====
    pdf.title_page()

    # ===== 目次 =====
    pdf.add_page()
    pdf.set_font(pdf.font_name, 'B', 18)
    pdf.set_text_color(55, 65, 81)
    pdf.cell(0, 14, '目次', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(6)

    toc = [
        ('1', 'システム概要', '機能と特徴'),
        ('2', 'アクセス方法', 'URLとログイン'),
        ('3', 'スタッフ向け操作ガイド', '希望シフトの提出方法'),
        ('4', '管理者向け操作ガイド', 'シフトの確認・確定方法'),
        ('5', 'シフトパターン一覧', '利用可能なパターン'),
        ('6', 'よくあるご質問（FAQ）', 'お困りの場合'),
    ]
    for num, title, desc in toc:
        pdf.set_font(pdf.font_name, 'B', 11)
        pdf.set_text_color(74, 144, 217)
        pdf.cell(10, 9, num, new_x='END')
        pdf.set_text_color(55, 65, 81)
        pdf.cell(80, 9, title, new_x='END')
        pdf.set_font(pdf.font_name, '', 9)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 9, desc, new_x='LMARGIN', new_y='NEXT')
        pdf.ln(1)

    # ===== 1. システム概要 =====
    pdf.add_page()
    pdf.section_title('1', 'システム概要')

    pdf.body_text(
        'シフト管理システムは、パート・アルバイトスタッフのシフト希望を'
        '簡単に収集・管理するためのWebアプリケーションです。'
        'スマートフォン・パソコンのどちらからでもご利用いただけます。'
    )

    pdf.sub_title('主な機能')
    pdf.bullet('スタッフがスマホからシフト希望を提出')
    pdf.bullet('カレンダー形式で直感的に日付を選択')
    pdf.bullet('早番・遅番などシフトパターンをワンタップで選択')
    pdf.bullet('管理者が一覧画面でシフト希望を確認・確定')
    pdf.bullet('確定したシフトをスタッフがリアルタイムで確認')
    pdf.bullet('人員の過不足を色分けで表示')

    pdf.sub_title('画面構成')
    pdf.bullet('トップページ: スタッフ用 / 管理者用の入口')
    pdf.bullet('スタッフ画面: カレンダーとシフト一覧')
    pdf.bullet('管理者画面: 全スタッフのシフトを日付×名前のグリッドで表示')

    # ===== 2. アクセス方法 =====
    pdf.add_page()
    pdf.section_title('2', 'アクセス方法')

    pdf.sub_title('アクセスURL')
    pdf.body_text(
        '下記のURLにスマートフォンまたはパソコンのブラウザからアクセスしてください。'
    )
    pdf.info_box('URL', '（管理者より共有されたURLをご利用ください）')

    pdf.sub_title('推奨ブラウザ')
    pdf.bullet('Google Chrome（推奨）')
    pdf.bullet('Safari（iPhone）')
    pdf.bullet('Microsoft Edge')

    pdf.sub_title('スマートフォンでのホーム画面追加（任意）')
    pdf.body_text('よく使う場合は、ホーム画面に追加すると便利です。')
    pdf.step(1, 'ブラウザでシステムのURLを開く')
    pdf.step(2, 'iPhoneの場合: 共有ボタン → 「ホーム画面に追加」')
    pdf.step(3, 'Androidの場合: メニュー → 「ホーム画面に追加」')

    # ===== 3. スタッフ向け操作ガイド =====
    pdf.add_page()
    pdf.section_title('3', 'スタッフ向け操作ガイド')

    pdf.sub_title('3-1. ログイン')
    pdf.step(1, 'トップページで「スタッフの方」をタップ')
    pdf.step(2, 'お名前を入力してログインをタップ')
    pdf.warning_box('毎回同じ名前でログインしてください。名前が変わると別人として登録されます。')

    pdf.sub_title('3-2. シフト希望の提出')
    pdf.step(1, 'カレンダーから希望する日付をタップ')
    pdf.step(2, 'シフトパターンを選択（早番・日勤・遅番など）')
    pdf.step(3, '必要に応じて時間を手動で調整')
    pdf.step(4, '備考があれば入力（例: 「午前のみ希望」）')
    pdf.step(5, '「この日のシフト希望を提出」をタップ')
    pdf.info_box('ポイント', 'パターンを選ぶと時間が自動入力されます。カスタム時間も設定できます。')

    pdf.sub_title('3-3. 提出済みシフトの確認')
    pdf.body_text(
        'カレンダー上のドット表示で状態がわかります。'
    )
    pdf.bullet('オレンジのドット → 申請中（まだ確定されていません）')
    pdf.bullet('緑のドット → 確定済み（出勤が決定しました）')
    pdf.body_text(
        'カレンダーの下には今月のシフト一覧が表示されます。'
    )

    pdf.sub_title('3-4. シフト希望の変更・取消')
    pdf.step(1, '変更したい日付をカレンダーでタップ')
    pdf.step(2, '時間を変更して再提出、または「この日の希望を取り消す」をタップ')
    pdf.warning_box('確定済みのシフトはスタッフ側では変更できません。管理者にご連絡ください。')

    pdf.sub_title('3-5. 月の切り替え')
    pdf.body_text(
        'カレンダー上部の「<」「>」ボタンで前月・翌月に移動できます。'
    )

    # ===== 4. 管理者向け操作ガイド =====
    pdf.add_page()
    pdf.section_title('4', '管理者向け操作ガイド')

    pdf.sub_title('4-1. ログイン')
    pdf.step(1, 'トップページで「管理者の方」をタップ')
    pdf.step(2, 'パスワードを入力してログイン')
    pdf.info_box('初期パスワード', 'admin123（セキュリティのため変更を推奨します）')

    pdf.sub_title('4-2. グリッド画面の見方')
    pdf.body_text(
        '管理画面では、横軸に日付、縦軸にスタッフ名のグリッド表示で'
        '全体のシフト状況を一目で確認できます。'
    )
    pdf.bullet('緑色のセル → シフト確定済み')
    pdf.bullet('黄色のセル → スタッフからの申請あり（未確定）')
    pdf.bullet('空白のセル → 申請なし')

    pdf.sub_title('4-3. 人員状況の確認')
    pdf.body_text(
        'グリッドの最下行に日ごとの確定人数が表示されます。'
    )
    pdf.bullet('緑色 → 必要人数を満たしています')
    pdf.bullet('黄色 → 申請含めれば人数を満たせます')
    pdf.bullet('赤色 → 人員が不足しています')

    pdf.sub_title('4-4. シフトの確定')
    pdf.body_text('方法1: グリッドのセルをタップ')
    pdf.step(1, '黄色いセル（申請中）をタップ')
    pdf.step(2, '内容を確認し「このシフトを確定」をタップ')
    pdf.ln(2)
    pdf.body_text('方法2: 未確定の申請一覧から確定')
    pdf.step(1, '画面下部の「未確定の申請」一覧を確認')
    pdf.step(2, '各申請の「確定」ボタンをタップ')

    pdf.sub_title('4-5. 確定の取り消し')
    pdf.step(1, '緑色のセル（確定済み）をタップ')
    pdf.step(2, '「確定を取り消す」をタップ')

    # ===== 5. シフトパターン一覧 =====
    pdf.add_page()
    pdf.section_title('5', 'シフトパターン一覧')

    pdf.body_text('以下のシフトパターンがあらかじめ登録されています。')
    pdf.ln(4)

    # テーブル
    pdf.set_font(pdf.font_name, 'B', 10)
    pdf.set_fill_color(74, 144, 217)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(50, 9, '  パターン名', fill=True, new_x='END')
    pdf.cell(45, 9, '  開始時間', fill=True, new_x='END')
    pdf.cell(45, 9, '  終了時間', fill=True, new_x='END')
    pdf.cell(30, 9, '  色', fill=True, new_x='LMARGIN', new_y='NEXT')

    patterns = [
        ('早番', '06:00', '14:00', '緑'),
        ('日勤', '09:00', '17:00', '青'),
        ('遅番', '14:00', '22:00', 'オレンジ'),
        ('夜勤', '22:00', '06:00', '紫'),
        ('午前', '09:00', '13:00', '水色'),
        ('午後', '13:00', '17:00', 'ピンク'),
    ]
    pdf.set_font(pdf.font_name, '', 10)
    for i, (name, start, end, color) in enumerate(patterns):
        if i % 2 == 0:
            pdf.set_fill_color(248, 249, 250)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(55, 65, 81)
        pdf.cell(50, 8, f'  {name}', fill=True, new_x='END')
        pdf.cell(45, 8, f'  {start}', fill=True, new_x='END')
        pdf.cell(45, 8, f'  {end}', fill=True, new_x='END')
        pdf.cell(30, 8, f'  {color}', fill=True, new_x='LMARGIN', new_y='NEXT')

    pdf.ln(6)
    pdf.info_box('カスタム時間', 'パターン以外の時間帯をご希望の場合は、時間を手動で入力できます。')

    # ===== 6. FAQ =====
    pdf.add_page()
    pdf.section_title('6', 'よくあるご質問（FAQ）')

    faqs = [
        ('Q. 名前を間違えてログインしてしまいました',
         'A. 一度ログアウトして、正しい名前で再度ログインしてください。間違った名前で提出したシフトは管理者にご連絡ください。'),
        ('Q. 同じ日に2つのシフトを出せますか？',
         'A. 1日に1つのシフト希望のみ提出できます。変更したい場合は同じ日を再度タップして上書きしてください。'),
        ('Q. 確定したシフトを変更したい場合は？',
         'A. 確定済みシフトの変更はスタッフ側からはできません。管理者にご連絡ください。'),
        ('Q. スマートフォンで見づらい場合は？',
         'A. 画面を横向きにするか、ブラウザの拡大縮小機能をお試しください。Chromeブラウザの使用を推奨します。'),
        ('Q. パスワードを変更したい（管理者）',
         'A. システム管理者にご連絡ください。サーバー側で変更いたします。'),
        ('Q. 過去の日付にシフトを入れられますか？',
         'A. 過去の日付は選択できない仕様になっています。当日以降の日付のみ選択可能です。'),
    ]
    for q, a in faqs:
        pdf.set_font(pdf.font_name, 'B', 10)
        pdf.set_text_color(74, 144, 217)
        pdf.cell(0, 7, q, new_x='LMARGIN', new_y='NEXT')
        pdf.set_font(pdf.font_name, '', 10)
        pdf.set_text_color(55, 65, 81)
        pdf.multi_cell(170, 7, a)
        pdf.ln(4)

    # 最終ページ: お問い合わせ
    pdf.ln(10)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.line(pdf.l_margin, pdf.get_y(), 200 - pdf.r_margin, pdf.get_y())
    pdf.ln(8)
    pdf.set_font(pdf.font_name, 'B', 12)
    pdf.set_text_color(55, 65, 81)
    pdf.cell(0, 10, 'お問い合わせ', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font(pdf.font_name, '', 10)
    pdf.body_text(
        'ご不明な点がございましたら、お気軽にお問い合わせください。\n'
        '担当: RH Technology'
    )

    # 保存
    pdf.output(OUTPUT_PATH)
    print(f'PDF created: {OUTPUT_PATH}')


if __name__ == '__main__':
    create_manual()
