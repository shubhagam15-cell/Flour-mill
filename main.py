import os
import sqlite3
from datetime import datetime
from urllib.parse import quote

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

APP_NAME = "श्री लक्ष्मी पिठाची गिरणी"

def db_path():
    return os.path.join(App.get_running_app().user_data_dir, "flourmill.db")

class FlourMillApp(App):
    title = APP_NAME

    def build(self):
        self.init_db()
        Window.softinput_mode = "below_target"
        self.root_box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        self.show_home()
        return self.root_box

    def init_db(self):
        os.makedirs(self.user_data_dir, exist_ok=True)
        con = sqlite3.connect(db_path())
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            customer TEXT NOT NULL,
            phone TEXT,
            grain TEXT NOT NULL,
            weight REAL NOT NULL,
            rate REAL NOT NULL,
            total REAL NOT NULL,
            paid REAL NOT NULL,
            payment_mode TEXT NOT NULL,
            balance REAL NOT NULL
        )""")
        con.commit()
        con.close()

    def clear(self):
        self.root_box.clear_widgets()

    def heading(self, text):
        return Label(text=text, size_hint_y=None, height=dp(48),
                     font_size="21sp", bold=True, color=(0.12, 0.30, 0.18, 1))

    def make_button(self, text, callback):
        b = Button(text=text, size_hint_y=None, height=dp(48), font_size="16sp")
        b.bind(on_release=callback)
        return b

    def show_home(self, *_):
        self.clear()
        self.root_box.add_widget(self.heading(APP_NAME))
        self.root_box.add_widget(Label(
            text="ऑफलाइन बिलिंग • ग्राहक खाते • रोजचा हिशोब",
            size_hint_y=None, height=dp(30), font_size="14sp"))
        con = sqlite3.connect(db_path())
        cur = con.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute("SELECT COUNT(*), COALESCE(SUM(weight),0), COALESCE(SUM(total),0), COALESCE(SUM(paid),0), COALESCE(SUM(balance),0) FROM bills WHERE substr(created_at,1,10)=?", (today,))
        count, kg, total, paid, balance = cur.fetchone()
        con.close()
        summary = (
            f"आजची बिले: {count}\nआजचे दळण: {kg:.2f} KG\n"
            f"आजची एकूण रक्कम: ₹{total:.2f}\nआज मिळालेले पैसे: ₹{paid:.2f}\n"
            f"आजची बाकी: ₹{balance:.2f}"
        )
        self.root_box.add_widget(Label(text=summary, size_hint_y=None, height=dp(150),
                                       font_size="17sp", halign="left", valign="middle"))
        self.root_box.add_widget(self.make_button("＋ नवीन बिल तयार करा", self.show_new_bill))
        self.root_box.add_widget(self.make_button("ग्राहकांचे खाते / जुनी बिले", self.show_ledger))
        self.root_box.add_widget(self.make_button("रिपोर्ट", self.show_reports))
        self.root_box.add_widget(Label(
            text="टीप: डेटा या मोबाईलमध्ये ऑफलाइन सेव्ह होतो. नियमित बॅकअप घ्या.",
            size_hint_y=None, height=dp(45), font_size="12sp"))

    def show_new_bill(self, *_):
        self.clear()
        self.root_box.add_widget(self.heading("नवीन बिल"))
        scroll = ScrollView()
        form = GridLayout(cols=1, spacing=dp(7), size_hint_y=None, padding=dp(4))
        form.bind(minimum_height=form.setter("height"))

        self.name_in = self.add_field(form, "ग्राहकाचे नाव *")
        self.phone_in = self.add_field(form, "मोबाईल नंबर (ऐच्छिक)", input_filter="int")
        self.grain_in = Spinner(text="गहू", values=("गहू", "ज्वारी", "बाजरी"),
                                size_hint_y=None, height=dp(46), font_size="16sp")
        form.add_widget(Label(text="धान्याचा प्रकार", size_hint_y=None, height=dp(25)))
        form.add_widget(self.grain_in)
        self.weight_in = self.add_field(form, "वजन (KG)", input_filter="float")
        self.rate_in = self.add_field(form, "दर (₹ प्रति KG)", input_filter="float")
        self.paid_in = self.add_field(form, "आता भरलेली रक्कम (₹)", input_filter="float")
        self.mode_in = Spinner(text="Cash", values=("Cash", "UPI", "PhonePe", "उधारी"),
                                size_hint_y=None, height=dp(46), font_size="16sp")
        form.add_widget(Label(text="पेमेंट पद्धत", size_hint_y=None, height=dp(25)))
        form.add_widget(self.mode_in)
        self.total_label = Label(text="एकूण: ₹0.00 | बाकी: ₹0.00",
                                 size_hint_y=None, height=dp(40), font_size="17sp", bold=True)
        form.add_widget(self.total_label)
        for field in (self.weight_in, self.rate_in, self.paid_in):
            field.bind(text=self.update_total)
        form.add_widget(self.make_button("बिल सेव्ह करा", self.save_bill))
        form.add_widget(self.make_button("मुख्य स्क्रीन", self.show_home))
        scroll.add_widget(form)
        self.root_box.add_widget(scroll)

    def add_field(self, parent, hint, input_filter=None):
        t = TextInput(hint_text=hint, multiline=False, size_hint_y=None,
                      height=dp(46), font_size="16sp", input_filter=input_filter)
        parent.add_widget(t)
        return t

    def num(self, widget):
        try:
            return float(widget.text or 0)
        except ValueError:
            return 0.0

    def update_total(self, *_):
        total = self.num(self.weight_in) * self.num(self.rate_in)
        paid = self.num(self.paid_in)
        self.total_label.text = f"एकूण: ₹{total:.2f} | बाकी: ₹{max(0,total-paid):.2f}"

    def save_bill(self, *_):
        customer = self.name_in.text.strip()
        if not customer:
            self.show_message("कृपया ग्राहकाचे नाव भरा.")
            return
        weight, rate, paid = self.num(self.weight_in), self.num(self.rate_in), self.num(self.paid_in)
        if weight <= 0 or rate < 0 or paid < 0:
            self.show_message("वजन, दर आणि भरलेली रक्कम तपासा.")
            return
        total = weight * rate
        if paid > total:
            self.show_message("भरलेली रक्कम एकूण बिलापेक्षा जास्त आहे.")
            return
        balance = total - paid
        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        values = (created, customer, self.phone_in.text.strip(), self.grain_in.text,
                  weight, rate, total, paid, self.mode_in.text, balance)
        con = sqlite3.connect(db_path())
        con.execute("""INSERT INTO bills(created_at,customer,phone,grain,weight,rate,total,paid,payment_mode,balance)
                       VALUES(?,?,?,?,?,?,?,?,?,?)""", values)
        con.commit()
        bill_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
        con.close()
        message = (f"{APP_NAME}\\nबिल क्रमांक: {bill_id}\\nदिनांक: {created}\\n"
                   f"ग्राहक: {customer}\\nधान्य: {self.grain_in.text}\\n"
                   f"वजन: {weight:g} KG\\nदर: ₹{rate:g}/KG\\n"
                   f"एकूण: ₹{total:.2f}\\nभरले: ₹{paid:.2f}\\n"
                   f"बाकी: ₹{balance:.2f}\\nधन्यवाद!")
        self.last_message = message
        self.last_phone = self.phone_in.text.strip()
        self.show_saved_bill(bill_id, message, total, paid, balance)

    def show_saved_bill(self, bill_id, message, total, paid, balance):
        self.clear()
        self.root_box.add_widget(self.heading("बिल सेव्ह झाले!"))
        self.root_box.add_widget(Label(
            text=f"बिल क्रमांक: {bill_id}\\nएकूण: ₹{total:.2f}\\nभरले: ₹{paid:.2f}\\nबाकी: ₹{balance:.2f}",
            size_hint_y=None, height=dp(130), font_size="18sp"))
        self.root_box.add_widget(self.make_button("WhatsApp मेसेज शेअर करा", self.share_whatsapp))
        self.root_box.add_widget(self.make_button("मुख्य स्क्रीन", self.show_home))
        self.root_box.add_widget(self.make_button("नवीन बिल", self.show_new_bill))

    def share_whatsapp(self, *_):
        # Opens Android share sheet; user selects WhatsApp and confirms sending.
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            String = autoclass("java.lang.String")
            intent = Intent(Intent.ACTION_SEND)
            intent.setType("text/plain")
            intent.putExtra(Intent.EXTRA_TEXT, String(self.last_message))
            chooser = Intent.createChooser(intent, String("WhatsApp वर बिल शेअर करा"))
            PythonActivity.mActivity.startActivity(chooser)
        except Exception:
            from kivy.utils import platform
            if platform == "android":
                self.show_message("शेअर सुविधा सुरू झाली नाही. Android build तपासा.")
            else:
                self.show_message("ही सुविधा Android मोबाईलवर चालेल.")

    def show_ledger(self, *_):
        self.clear()
        self.root_box.add_widget(self.heading("ग्राहकांचे खाते / जुनी बिले"))
        con = sqlite3.connect(db_path())
        rows = con.execute("""SELECT customer, phone, COUNT(*), SUM(total), SUM(paid), SUM(balance)
                              FROM bills GROUP BY customer ORDER BY customer""").fetchall()
        con.close()
        scroll = ScrollView()
        box = GridLayout(cols=1, spacing=dp(6), size_hint_y=None, padding=dp(4))
        box.bind(minimum_height=box.setter("height"))
        if not rows:
            box.add_widget(Label(text="अजून कोणतेही बिल नाही.", size_hint_y=None, height=dp(45)))
        for name, phone, count, total, paid, balance in rows:
            box.add_widget(Label(
                text=f"{name}  |  बिले: {count}\\nमोबाईल: {phone or '-'}\\n"
                     f"एकूण: ₹{total:.2f}  भरले: ₹{paid:.2f}  बाकी: ₹{balance:.2f}",
                size_hint_y=None, height=dp(95), font_size="14sp"))
        scroll.add_widget(box)
        self.root_box.add_widget(scroll)
        self.root_box.add_widget(self.make_button("मुख्य स्क्रीन", self.show_home))

    def show_reports(self, *_):
        self.clear()
        self.root_box.add_widget(self.heading("रिपोर्ट"))
        con = sqlite3.connect(db_path())
        rows = con.execute("""SELECT substr(created_at,1,7), COUNT(*), SUM(weight), SUM(total), SUM(paid), SUM(balance)
                              FROM bills GROUP BY substr(created_at,1,7) ORDER BY 1 DESC""").fetchall()
        con.close()
        scroll = ScrollView()
        box = GridLayout(cols=1, spacing=dp(6), size_hint_y=None, padding=dp(4))
        box.bind(minimum_height=box.setter("height"))
        if not rows:
            box.add_widget(Label(text="रिपोर्टसाठी व्यवहार उपलब्ध नाहीत.", size_hint_y=None, height=dp(45)))
        for month, count, kg, total, paid, balance in rows:
            box.add_widget(Label(
                text=f"महिना: {month}\\nबिले: {count} | दळण: {kg:.2f} KG\\n"
                     f"विक्री: ₹{total:.2f} | मिळाले: ₹{paid:.2f}\\nबाकी: ₹{balance:.2f}",
                size_hint_y=None, height=dp(105), font_size="14sp"))
        scroll.add_widget(box)
        self.root_box.add_widget(scroll)
        self.root_box.add_widget(self.make_button("मुख्य स्क्रीन", self.show_home))

    def show_message(self, message):
        from kivy.uix.popup import Popup
        Popup(title="माहिती", content=Label(text=message), size_hint=(0.85, 0.35)).open()

if __name__ == "__main__":
    FlourMillApp().run()
