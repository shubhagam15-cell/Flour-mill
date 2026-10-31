# श्री लक्ष्मी पिठाची गिरणी — Android App (पहिला नमुना)

हा पहिला ऑफलाइन नमुना आहे. यात:
- ग्राहकाचे नाव, मोबाईल, धान्य, वजन, दर
- एकूण रक्कम व बाकीची स्वयंचलित गणना
- Cash / UPI / PhonePe / उधारी नोंद
- SQLite मध्ये ऑफलाइन बिल सेव्ह
- ग्राहकनिहाय एकूण खाते
- महिन्यानिहाय रिपोर्ट
- Android Share Sheet मधून WhatsApp वर बिलाचा मजकूर शेअर

## महत्त्वाच्या मर्यादा
- WhatsApp मेसेज आपोआप पाठवला जात नाही; वापरकर्ता WhatsApp निवडून Send करतो.
- हा पहिला prototype आहे. PDF/प्रिंट, डेटा बॅकअप/रीस्टोर, ग्राहकाचे स्वतंत्र व्यवहार तपशील आणि सुरक्षिततेची चाचणी पुढील आवृत्तीत जोडायची आहे.
- PDF मधील मराठी अक्षरांसाठी Devanagari Unicode font जोडणे आवश्यक आहे.
- फोन बदलण्यापूर्वी डेटाबेसचा बॅकअप घेणे आवश्यक आहे.

## Android APK तयार करण्यासाठी
Buildozer साधारणपणे Linux किंवा WSL (Windows) वर वापरतात.

1. Python 3 आणि Buildozer/Android build dependencies install करा.
2. या फोल्डरमध्ये terminal उघडा.
3. चालवा:
   ```bash
   buildozer android debug
   ```
4. तयार APK `bin/` फोल्डरमध्ये मिळेल.
5. APK स्वतःच्या Android फोनवर install करा.

Buildozer अधिकृत मार्गदर्शक: https://buildozer.readthedocs.io/

## संगणकावर चाचणी
```bash
pip install kivy
python main.py
```
Desktop वर WhatsApp share बटण Android-only असल्याने माहिती दाखवेल.

## दर बदलणे
प्रत्येक नवीन बिलात धान्य निवडा आणि त्या बिलासाठी किलोचा दर भरा.
