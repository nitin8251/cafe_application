import streamlit as st

from components.service_form import (
    render_browser_camera_capture,
    render_custom_inputs,
    render_document_uploader,
    render_live_camera,
    render_optional_notes,
    render_other_documents_uploader,
    summarize_custom_inputs,
    validate_custom_inputs,
)
from components.ui import render_page_intro
from components.upload_sections import (
    DEFAULT_COLOR_MODE,
    PRINT_STYLE_OPTIONS,
    apply_upload_page_styles,
    build_file_overrides,
    render_jpg_to_pdf_fields,
    render_photo_service_fields,
)
from services.catalog import get_service_catalog, get_service_groups
from services.upload_helpers import (
    estimate_upload_total,
    filter_service_names,
    multiplier_price,
    service_suggestions,
    service_variant_options,
    slab_price,
)
from services.upload_service import submit_uploads


NOTES_SERVICE_GROUPS = {"desk", "scan", "utility", "rental"}
LANGUAGE_OPTIONS = {"en": "English", "hi": "हिन्दी", "mr": "मराठी"}
UPLOAD_TRANSLATIONS = {
    "Create Service Order": {"hi": "सेवा ऑर्डर बनाएं", "mr": "सेवा ऑर्डर तयार करा"},
    "Search the required service, check the document checklist, and create one clean order batch. Only the fields needed for the chosen service are shown.": {
        "hi": "ज़रूरी सेवा खोजें, दस्तावेज़ सूची देखें और एक साफ़ ऑर्डर बैच बनाएं। केवल चुनी गई सेवा के लिए आवश्यक फ़ील्ड दिखेंगी।",
        "mr": "आवश्यक सेवा शोधा, कागदपत्रांची यादी तपासा आणि एक स्वच्छ ऑर्डर बॅच तयार करा. निवडलेल्या सेवेसाठी लागणारीच फील्ड्स दिसतील।",
    },
    "Customer Desk": {"hi": "ग्राहक डेस्क", "mr": "ग्राहक डेस्क"},
    "Language": {"hi": "भाषा", "mr": "भाषा"},
    "All services": {"hi": "सभी सेवाएं", "mr": "सर्व सेवा"},
    "Service category": {"hi": "सेवा श्रेणी", "mr": "सेवा विभाग"},
    "Search service": {"hi": "सेवा खोजें", "mr": "सेवा शोधा"},
    "Search Aadhaar, PAN, photo, rental...": {"hi": "आधार, पैन, फोटो, रेंटल खोजें...", "mr": "आधार, पॅन, फोटो, रेंटल शोधा..."},
    "No services matched that search. Try a different keyword.": {"hi": "इस खोज से कोई सेवा नहीं मिली। दूसरा शब्द आज़माएं।", "mr": "या शोधाशी जुळणारी सेवा सापडली नाही. दुसरा शब्द वापरून पहा."},
    "Quick picks": {"hi": "त्वरित विकल्प", "mr": "जलद पर्याय"},
    "Service": {"hi": "सेवा", "mr": "सेवा"},
    "Service option": {"hi": "सेवा विकल्प", "mr": "सेवा पर्याय"},
    "Customer name": {"hi": "ग्राहक का नाम", "mr": "ग्राहकाचे नाव"},
    "Enter customer name": {"hi": "ग्राहक का नाम लिखें", "mr": "ग्राहकाचे नाव लिहा"},
    "Phone number": {"hi": "फोन नंबर", "mr": "फोन नंबर"},
    "Enter customer phone number": {"hi": "ग्राहक का फोन नंबर लिखें", "mr": "ग्राहकाचा फोन नंबर लिहा"},
    "Phone number is required for every order.": {"hi": "हर ऑर्डर के लिए फोन नंबर आवश्यक है।", "mr": "प्रत्येक ऑर्डरसाठी फोन नंबर आवश्यक आहे."},
    "Required Document Uploads": {"hi": "ज़रूरी दस्तावेज़ अपलोड", "mr": "आवश्यक कागदपत्र अपलोड"},
    "Upload the exact documents this service needs.": {"hi": "इस सेवा के लिए आवश्यक सही दस्तावेज़ अपलोड करें।", "mr": "या सेवेसाठी लागणारी नेमकी कागदपत्रे अपलोड करा."},
    "Upload the matching document beside each checklist item wherever it is available.": {"hi": "जहाँ संभव हो, हर सूची आइटम के सामने संबंधित दस्तावेज़ अपलोड करें।", "mr": "जिथे शक्य असेल तिथे प्रत्येक यादी आयटमसमोर संबंधित कागदपत्र अपलोड करा."},
    "Optional Document Upload": {"hi": "वैकल्पिक दस्तावेज़ अपलोड", "mr": "ऐच्छिक कागदपत्र अपलोड"},
    "Only upload the extra supporting document if the customer wants to attach it now.": {"hi": "केवल तभी अतिरिक्त दस्तावेज़ अपलोड करें जब ग्राहक अभी जोड़ना चाहता हो।", "mr": "ग्राहकाला आत्ता जोडायचे असल्यासच अतिरिक्त कागदपत्र अपलोड करा."},
    "Choose file(s)": {"hi": "फ़ाइल चुनें", "mr": "फाइल निवडा"},
    "Attach supporting file(s) if available": {"hi": "यदि उपलब्ध हों तो सहायक फ़ाइलें जोड़ें", "mr": "उपलब्ध असल्यास सहाय्यक फाइल्स जोडा"},
    "Service rate": {"hi": "सेवा शुल्क", "mr": "सेवा दर"},
    "Use this when the desk needs to override the listed rate for this job.": {"hi": "जब इस काम के लिए सूचीबद्ध दर बदलनी हो तब इसका उपयोग करें।", "mr": "या कामासाठी सूचीतील दर बदलायचा असल्यास हे वापरा."},
    "Notes": {"hi": "नोट्स", "mr": "नोंदी"},
    "+ Add notes": {"hi": "+ नोट्स जोड़ें", "mr": "+ नोंदी जोडा"},
    "Close notes": {"hi": "नोट्स बंद करें", "mr": "नोंदी बंद करा"},
    "Add application details, page notes, payment notes, or pickup instructions.": {"hi": "आवेदन विवरण, पेज नोट्स, भुगतान नोट्स या पिकअप निर्देश जोड़ें।", "mr": "अर्ज तपशील, पेज नोट्स, पेमेंट नोट्स किंवा पिकअप सूचना जोडा."},
    "Estimated bill": {"hi": "अनुमानित बिल", "mr": "अंदाजित बिल"},
    "This is a desk service. A file is optional, so you can create the order even without attachments.": {"hi": "यह डेस्क सेवा है। फ़ाइल वैकल्पिक है, इसलिए बिना अटैचमेंट भी ऑर्डर बना सकते हैं।", "mr": "ही डेस्क सेवा आहे. फाइल ऐच्छिक आहे, त्यामुळे अटॅचमेंट नसतानाही ऑर्डर तयार करू शकता."},
    "Option": {"hi": "विकल्प", "mr": "पर्याय"},
    "Bill amount": {"hi": "बिल राशि", "mr": "बिल रक्कम"},
    "Print style": {"hi": "प्रिंट स्टाइल", "mr": "प्रिंट स्टाइल"},
    "Mode": {"hi": "मोड", "mr": "मोड"},
    "Create order": {"hi": "ऑर्डर बनाएं", "mr": "ऑर्डर तयार करा"},
    "Please enter the customer name.": {"hi": "कृपया ग्राहक का नाम लिखें।", "mr": "कृपया ग्राहकाचे नाव लिहा."},
    "Please enter the phone number.": {"hi": "कृपया फोन नंबर लिखें।", "mr": "कृपया फोन नंबर लिहा."},
    "Please upload at least one supporting file for this service.": {"hi": "इस सेवा के लिए कम से कम एक फ़ाइल अपलोड करें।", "mr": "या सेवेसाठी किमान एक फाइल अपलोड करा."},
    "Please upload at least one portrait photo.": {"hi": "कृपया कम से कम एक फोटो अपलोड करें।", "mr": "कृपया किमान एक फोटो अपलोड करा."},
    "Order created. Pickup code": {"hi": "ऑर्डर बन गया। पिकअप कोड", "mr": "ऑर्डर तयार झाला. पिकअप कोड"},
    "item(s) queued for": {"hi": "आइटम कतार में जोड़े गए", "mr": "आयटम रांगेत जोडले गेले"},
    "file(s) stored successfully in local Streamlit storage.": {"hi": "फ़ाइलें स्थानीय स्ट्रीमलिट स्टोरेज में सुरक्षित हो गईं।", "mr": "फाइल्स स्थानिक स्ट्रीमलिट स्टोरेजमध्ये जतन झाल्या."},
    "This service was saved as a counter request without file storage.": {"hi": "यह सेवा बिना फ़ाइल स्टोरेज के काउंटर अनुरोध के रूप में सहेजी गई।", "mr": "ही सेवा फाइल स्टोरेजशिवाय काउंटर विनंती म्हणून जतन झाली."},
    "Repeat customer detected. Added to priority follow-up.": {"hi": "दोबारा आने वाले ग्राहक का पता चला। प्राथमिक फॉलो-अप में जोड़ा गया।", "mr": "पुन्हा येणारा ग्राहक ओळखला. प्राधान्य फॉलो-अपमध्ये जोडला."},
    "Amount": {"hi": "राशि", "mr": "रक्कम"},
    "Units": {"hi": "इकाइयाँ", "mr": "युनिट्स"},
    "Upload": {"hi": "अपलोड", "mr": "अपलोड"},
    "Take photo": {"hi": "फोटो लें", "mr": "फोटो घ्या"},
    "Take document photo": {"hi": "डॉक्यूमेंट फोटो लें", "mr": "डॉक्युमेंट फोटो घ्या"},
    "Take photo for other document": {"hi": "अन्य दस्तावेज़ की फोटो लें", "mr": "इतर कागदपत्राचा फोटो घ्या"},
    "Crop image": {"hi": "इमेज क्रॉप करें", "mr": "इमेज क्रॉप करा"},
    "Convert image to PDF": {"hi": "इमेज को PDF बनाएं", "mr": "इमेज PDF मध्ये बदला"},
    "Resize / compress image": {"hi": "इमेज रीसाइज / कंप्रेस करें", "mr": "इमेज रीसाइज / कॉम्प्रेस करा"},
    "Target size (KB)": {"hi": "लक्ष्य साइज (KB)", "mr": "लक्ष्य साइज (KB)"},
    "Attached": {"hi": "अटैच किया", "mr": "जोडले"},
    "Prepared": {"hi": "तैयार", "mr": "तयार"},
    "target": {"hi": "लक्ष्य", "mr": "लक्ष्य"},
    "No file attached yet": {"hi": "अभी कोई फाइल अटैच नहीं", "mr": "अजून कोणतीही फाइल जोडलेली नाही"},
    "No file attached": {"hi": "कोई फाइल अटैच नहीं", "mr": "फाइल जोडलेली नाही"},
    "Other Documents": {"hi": "अन्य दस्तावेज़", "mr": "इतर कागदपत्रे"},
    "Upload other documents": {"hi": "अन्य दस्तावेज़ अपलोड करें", "mr": "इतर कागदपत्रे अपलोड करा"},
    "Upload any extra files that do not fit into the listed requirement boxes. These files will be added to the same order.": {
        "hi": "जो अतिरिक्त फाइलें सूची में फिट नहीं होतीं उन्हें यहां अपलोड करें। ये उसी ऑर्डर में जुड़ेंगी।",
        "mr": "यादीत न बसणाऱ्या अतिरिक्त फाइल्स येथे अपलोड करा. त्या त्याच ऑर्डरमध्ये जोडल्या जातील.",
    },
    "Label for extra file": {"hi": "अतिरिक्त फाइल का लेबल", "mr": "अतिरिक्त फाइल लेबल"},
    "Other document, receipt, reference proof...": {"hi": "अन्य दस्तावेज़, रसीद, रेफरेंस प्रूफ...", "mr": "इतर कागदपत्र, पावती, रेफरन्स पुरावा..."},
    "Service Details": {"hi": "सेवा विवरण", "mr": "सेवा तपशील"},
    "Only the inputs configured for this service are shown here.": {"hi": "इस सेवा के लिए बनाए गए इनपुट ही यहां दिखेंगे।", "mr": "या सेवेसाठी कॉन्फिगर केलेले इनपुटच येथे दिसतील."},
    "Required field": {"hi": "ज़रूरी फ़ील्ड", "mr": "आवश्यक फील्ड"},
    "File-wise Settings": {"hi": "फाइल-वाइज सेटिंग्स", "mr": "फाइलनुसार सेटिंग्स"},
    "Adjust each file neatly here. Copies, print side, and color mode stay grouped under the same order.": {
        "hi": "हर फाइल की कॉपी, प्रिंट साइड और कलर मोड यहां सेट करें। सब एक ही ऑर्डर में रहेंगे।",
        "mr": "प्रत्येक फाइलची कॉपी, प्रिंट साइड आणि कलर मोड येथे सेट करा. सर्व एकाच ऑर्डरमध्ये राहतील.",
    },
    "Document Label": {"hi": "दस्तावेज़ लेबल", "mr": "कागदपत्र लेबल"},
    "Copies": {"hi": "कॉपी", "mr": "कॉपी"},
    "Side": {"hi": "साइड", "mr": "बाजू"},
    "Aadhaar card": {"hi": "आधार कार्ड", "mr": "आधार कार्ड"},
    "PDF output": {"hi": "PDF आउटपुट", "mr": "PDF आउटपुट"},
    "Merge into one PDF": {"hi": "एक PDF में मर्ज करें", "mr": "एकाच PDF मध्ये मर्ज करा"},
    "Separate PDFs": {"hi": "अलग-अलग PDF", "mr": "वेगवेगळे PDF"},
    "Compress images before PDF": {"hi": "PDF से पहले इमेज कंप्रेस करें", "mr": "PDF आधी इमेज कॉम्प्रेस करा"},
    "Target size per image (KB)": {"hi": "हर इमेज का लक्ष्य साइज (KB)", "mr": "प्रत्येक इमेजचा लक्ष्य साइज (KB)"},
    "Conversion notes": {"hi": "कन्वर्ज़न नोट्स", "mr": "कन्वर्जन नोंदी"},
    "Photo size preset": {"hi": "फोटो साइज प्रीसेट", "mr": "फोटो साइज प्रीसेट"},
    "Number of photos": {"hi": "फोटो की संख्या", "mr": "फोटो संख्या"},
    "Background / finish": {"hi": "बैकग्राउंड / फिनिश", "mr": "पार्श्वभूमी / फिनिश"},
    "Photo footer fields": {"hi": "फोटो के नीचे की जानकारी", "mr": "फोटोखालील माहिती"},
    "Choose footer items to print below each photo": {"hi": "हर फोटो के नीचे छापने वाली जानकारी चुनें", "mr": "प्रत्येक फोटोखाली छापायची माहिती निवडा"},
    "Name": {"hi": "नाम", "mr": "नाव"},
    "Name on photo": {"hi": "फोटो पर नाम", "mr": "फोटोवरील नाव"},
    "Download format": {"hi": "डाउनलोड फॉर्मेट", "mr": "डाउनलोड फॉरमॅट"},
    "JPG is better for smaller files. PDF is better for printing and sharing.": {
        "hi": "छोटी फाइल के लिए JPG बेहतर है। प्रिंट/शेयर के लिए PDF बेहतर है।",
        "mr": "लहान फाइलसाठी JPG चांगले. प्रिंट/शेअरिंगसाठी PDF चांगले.",
    },
    "Rate": {"hi": "रेट", "mr": "दर"},
    "Cut Size": {"hi": "कट साइज", "mr": "कट साइज"},
    "Printable Sheet Preview": {"hi": "प्रिंटेबल शीट प्रीव्यू", "mr": "प्रिंटेबल शीट प्रीव्यू"},
    "Sheet file": {"hi": "शीट फाइल", "mr": "शीट फाइल"},
    "Copies on one sheet": {"hi": "एक शीट पर कॉपी", "mr": "एका शीटवरील कॉपी"},
    "Grid": {"hi": "ग्रिड", "mr": "ग्रिड"},
    "Output": {"hi": "आउटपुट", "mr": "आउटपुट"},
    "Generated size": {"hi": "तैयार साइज", "mr": "तयार साइज"},
    "print": {"hi": "प्रिंट", "mr": "प्रिंट"},
    "government": {"hi": "सरकारी सेवाएं", "mr": "सरकारी सेवा"},
    "finishing": {"hi": "फिनिशिंग", "mr": "फिनिशिंग"},
    "utility": {"hi": "बिल / उपयोगिता", "mr": "बिल / युटिलिटी"},
    "rental": {"hi": "किराया सेवा", "mr": "भाडे सेवा"},
    "desk": {"hi": "डेस्क सेवा", "mr": "डेस्क सेवा"},
    "photo": {"hi": "फोटो सेवा", "mr": "फोटो सेवा"},
    "scan": {"hi": "स्कैन सेवा", "mr": "स्कॅन सेवा"},
    "Document Print / Xerox": {"hi": "डॉक्यूमेंट प्रिंट / ज़ेरॉक्स", "mr": "डॉक्युमेंट प्रिंट / झेरॉक्स"},
    "Senior Citizen Card": {"hi": "सीनियर सिटीजन कार्ड", "mr": "ज्येष्ठ नागरिक कार्ड"},
    "Aadhaar Address Update": {"hi": "आधार पता अपडेट", "mr": "आधार पत्ता अपडेट"},
    "PAN Card": {"hi": "पैन कार्ड", "mr": "पॅन कार्ड"},
    "Ayushman Card": {"hi": "आयुष्मान कार्ड", "mr": "आयुष्मान कार्ड"},
    "Property Card": {"hi": "प्रॉपर्टी कार्ड", "mr": "प्रॉपर्टी कार्ड"},
    "Udyam Aadhaar": {"hi": "उद्यम आधार", "mr": "उद्यम आधार"},
    "Driving Licence": {"hi": "ड्राइविंग लाइसेंस", "mr": "ड्रायव्हिंग लायसन्स"},
    "Lamination": {"hi": "लैमिनेशन", "mr": "लॅमिनेशन"},
    "Electricity Bill Payment": {"hi": "बिजली बिल भुगतान", "mr": "वीज बिल भरणा"},
    "Mobile Recharge Service": {"hi": "मोबाइल रिचार्ज सेवा", "mr": "मोबाइल रिचार्ज सेवा"},
    "Money Transfer Service": {"hi": "मनी ट्रांसफर सेवा", "mr": "मनी ट्रान्सफर सेवा"},
    "Bike Rental": {"hi": "बाइक किराया", "mr": "बाईक भाडे"},
    "Car Rental": {"hi": "कार किराया", "mr": "कार भाडे"},
    "Government Exam Form": {"hi": "सरकारी परीक्षा फॉर्म", "mr": "सरकारी परीक्षा फॉर्म"},
    "Photo Paper Sheet": {"hi": "फोटो पेपर शीट", "mr": "फोटो पेपर शीट"},
    "Passport Photo Print": {"hi": "पासपोर्ट फोटो प्रिंट", "mr": "पासपोर्ट फोटो प्रिंट"},
    "JPG to PDF": {"hi": "JPG से PDF", "mr": "JPG ते PDF"},
    "Scan to PDF": {"hi": "स्कैन से PDF", "mr": "स्कॅन ते PDF"},
    "Typing / Form Fill": {"hi": "टाइपिंग / फॉर्म भरना", "mr": "टायपिंग / फॉर्म भरणे"},
    "Passport Renewal": {"hi": "पासपोर्ट रिन्यूअल", "mr": "पासपोर्ट नूतनीकरण"},
    "Single counter flow for document printing and xerox work. Choose black and white or color per file.": {
        "hi": "डॉक्यूमेंट प्रिंट और ज़ेरॉक्स के लिए एक ही काउंटर फ्लो। हर फाइल के लिए ब्लैक एंड व्हाइट या कलर चुनें।",
        "mr": "डॉक्युमेंट प्रिंट आणि झेरॉक्ससाठी एकच काउंटर फ्लो. प्रत्येक फाइलसाठी ब्लॅक अँड व्हाइट किंवा कलर निवडा.",
    },
    "Senior citizen card application and support service.": {"hi": "सीनियर सिटीजन कार्ड आवेदन और सहायता सेवा।", "mr": "ज्येष्ठ नागरिक कार्ड अर्ज आणि सहाय्य सेवा."},
    "Address update assistance for Aadhaar-related service work.": {"hi": "आधार से जुड़ी पता अपडेट सहायता।", "mr": "आधार संबंधित पत्ता अपडेट सहाय्य."},
    "PAN card application and correction support.": {"hi": "पैन कार्ड आवेदन और सुधार सहायता।", "mr": "पॅन कार्ड अर्ज आणि दुरुस्ती सहाय्य."},
    "Ayushman card service and beneficiary support.": {"hi": "आयुष्मान कार्ड और लाभार्थी सहायता सेवा।", "mr": "आयुष्मान कार्ड आणि लाभार्थी सहाय्य सेवा."},
    "Property card download or service request support.": {"hi": "प्रॉपर्टी कार्ड डाउनलोड या सेवा अनुरोध सहायता।", "mr": "प्रॉपर्टी कार्ड डाउनलोड किंवा सेवा विनंती सहाय्य."},
    "Udyam registration and Aadhaar-linked business service support.": {"hi": "उद्यम रजिस्ट्रेशन और आधार-लिंक्ड बिज़नेस सहायता।", "mr": "उद्यम नोंदणी आणि आधार-लिंक्ड व्यवसाय सहाय्य."},
    "Licence application help. Update the exact rate from the desk if needed.": {"hi": "लाइसेंस आवेदन सहायता। जरूरत हो तो डेस्क से सही रेट अपडेट करें।", "mr": "लायसन्स अर्ज सहाय्य. गरज असल्यास डेस्कवरून योग्य दर अपडेट करा."},
    "Card and A4 lamination options with or without print.": {"hi": "प्रिंट के साथ या बिना कार्ड और A4 लैमिनेशन विकल्प।", "mr": "प्रिंटसह किंवा शिवाय कार्ड आणि A4 लॅमिनेशन पर्याय."},
    "Electricity bill service charge based on Rs. 20 per Rs. 1000 bill slab.": {"hi": "बिजली बिल सेवा शुल्क Rs. 1000 स्लैब पर Rs. 20 के हिसाब से।", "mr": "वीज बिल सेवा शुल्क Rs. 1000 स्लॅबला Rs. 20 प्रमाणे."},
    "Recharge handling or recharge support service charge.": {"hi": "रिचार्ज हैंडलिंग या रिचार्ज सहायता सेवा शुल्क।", "mr": "रिचार्ज हाताळणी किंवा रिचार्ज सहाय्य सेवा शुल्क."},
    "Money transfer service charge based on Rs. 20 per Rs. 1000 transfer slab.": {"hi": "मनी ट्रांसफर सेवा शुल्क Rs. 1000 स्लैब पर Rs. 20 के हिसाब से।", "mr": "मनी ट्रान्सफर सेवा शुल्क Rs. 1000 स्लॅबला Rs. 20 प्रमाणे."},
    "Bike rental charged at Rs. 500 per day.": {"hi": "बाइक किराया Rs. 500 प्रति दिन।", "mr": "बाईक भाडे Rs. 500 प्रति दिवस."},
    "Car rental charged at Rs. 15 per km.": {"hi": "कार किराया Rs. 15 प्रति किमी।", "mr": "कार भाडे Rs. 15 प्रति किमी."},
    "Exam form filling support. Online fee is extra and should be noted separately.": {"hi": "परीक्षा फॉर्म भरने की सहायता। ऑनलाइन फीस अलग है और अलग से नोट करें।", "mr": "परीक्षा फॉर्म भरण्यास सहाय्य. ऑनलाइन फी वेगळी असून स्वतंत्र नोंद करा."},
    "Photo paper or color-point card job. Update size-specific pricing if needed.": {"hi": "फोटो पेपर या कलर-पॉइंट कार्ड कार्य। जरूरत हो तो साइज के अनुसार रेट अपडेट करें।", "mr": "फोटो पेपर किंवा कलर-पॉइंट कार्ड काम. गरज असल्यास साइजप्रमाणे दर अपडेट करा."},
    "Create passport or visa-style photo sheets directly from an uploaded portrait.": {"hi": "अपलोड फोटो से पासपोर्ट या वीज़ा स्टाइल फोटो शीट बनाएं।", "mr": "अपलोड फोटोवरून पासपोर्ट किंवा व्हिसा स्टाइल फोटो शीट तयार करा."},
    "Convert one or more JPG or image files into a single PDF document.": {"hi": "एक या अधिक JPG / इमेज फाइलों को एक PDF में बदलें।", "mr": "एक किंवा अधिक JPG / इमेज फाइल्स एकाच PDF मध्ये बदला."},
    "Scan physical pages into a single PDF or image set.": {"hi": "फिजिकल पेज स्कैन करके PDF या इमेज सेट बनाएं।", "mr": "फिजिकल पेज स्कॅन करून PDF किंवा इमेज सेट तयार करा."},
    "Typing, drafting, and basic data-entry desk service.": {"hi": "टाइपिंग, ड्राफ्टिंग और बेसिक डेटा-एंट्री डेस्क सेवा।", "mr": "टायपिंग, ड्राफ्टिंग आणि बेसिक डेटा-एंट्री डेस्क सेवा."},
    "New passport Issuance": {"hi": "नया पासपोर्ट जारी करने की सेवा।", "mr": "नवीन पासपोर्ट जारी सेवा."},
    "Upload the document to print or copy": {"hi": "प्रिंट या कॉपी के लिए डॉक्यूमेंट अपलोड करें", "mr": "प्रिंट किंवा कॉपीसाठी डॉक्युमेंट अपलोड करा"},
    "Set copies and print style for each file": {"hi": "हर फाइल के लिए कॉपी और प्रिंट स्टाइल सेट करें", "mr": "प्रत्येक फाइलसाठी कॉपी आणि प्रिंट स्टाइल सेट करा"},
    "Choose black and white or color per file": {"hi": "हर फाइल के लिए ब्लैक एंड व्हाइट या कलर चुनें", "mr": "प्रत्येक फाइलसाठी ब्लॅक अँड व्हाइट किंवा कलर निवडा"},
    "Mention any page range or special notes": {"hi": "पेज रेंज या विशेष नोट्स लिखें", "mr": "पेज रेंज किंवा विशेष नोंदी लिहा"},
    "Aadhaar card copy": {"hi": "आधार कार्ड कॉपी", "mr": "आधार कार्ड कॉपी"},
    "Age proof document": {"hi": "उम्र प्रमाण दस्तावेज़", "mr": "वयाचा पुरावा"},
    "Passport-size photo": {"hi": "पासपोर्ट साइज फोटो", "mr": "पासपोर्ट साइज फोटो"},
    "Mobile number": {"hi": "मोबाइल नंबर", "mr": "मोबाइल नंबर"},
    "Aadhaar number or Aadhaar copy": {"hi": "आधार नंबर या आधार कॉपी", "mr": "आधार नंबर किंवा आधार कॉपी"},
    "Address proof": {"hi": "पता प्रमाण", "mr": "पत्ता पुरावा"},
    "Registered mobile number": {"hi": "रजिस्टर्ड मोबाइल नंबर", "mr": "नोंदणीकृत मोबाइल नंबर"},
    "Recent passport-size photo if required": {"hi": "जरूरत हो तो हाल की पासपोर्ट फोटो", "mr": "गरज असल्यास अलीकडील पासपोर्ट फोटो"},
    "Signature specimen": {"hi": "हस्ताक्षर नमूना", "mr": "स्वाक्षरी नमुना"},
    "Aadhaar card": {"hi": "आधार कार्ड", "mr": "आधार कार्ड"},
    "Ration card or family ID": {"hi": "राशन कार्ड या फैमिली ID", "mr": "रेशन कार्ड किंवा फॅमिली ID"},
    "Property or survey details": {"hi": "प्रॉपर्टी या सर्वे विवरण", "mr": "प्रॉपर्टी किंवा सर्वे तपशील"},
    "Village / ward details": {"hi": "गांव / वार्ड विवरण", "mr": "गाव / वॉर्ड तपशील"},
    "Owner name": {"hi": "मालिक का नाम", "mr": "मालकाचे नाव"},
    "PAN card": {"hi": "पैन कार्ड", "mr": "पॅन कार्ड"},
    "Business address details": {"hi": "बिज़नेस पता विवरण", "mr": "व्यवसाय पत्ता तपशील"},
    "Bank details and mobile number": {"hi": "बैंक विवरण और मोबाइल नंबर", "mr": "बँक तपशील आणि मोबाइल नंबर"},
    "Existing licence details if applicable": {"hi": "यदि लागू हो तो मौजूदा लाइसेंस विवरण", "mr": "लागू असल्यास विद्यमान लायसन्स तपशील"},
    "Printed document or card to laminate": {"hi": "लैमिनेशन के लिए प्रिंटेड डॉक्यूमेंट या कार्ड", "mr": "लॅमिनेशनसाठी प्रिंटेड डॉक्युमेंट किंवा कार्ड"},
    "Mention lamination size needed": {"hi": "लैमिनेशन साइज लिखें", "mr": "लॅमिनेशन साइज लिहा"},
    "Ask the desk if print is also required": {"hi": "प्रिंट भी चाहिए तो डेस्क को बताएं", "mr": "प्रिंटही हवे असल्यास डेस्कला सांगा"},
    "Consumer number": {"hi": "कंज्यूमर नंबर", "mr": "ग्राहक क्रमांक"},
    "Bill copy or bill amount": {"hi": "बिल कॉपी या बिल राशि", "mr": "बिल कॉपी किंवा बिल रक्कम"},
    "Payment amount": {"hi": "भुगतान राशि", "mr": "पेमेंट रक्कम"},
    "Mobile number for receipt": {"hi": "रसीद के लिए मोबाइल नंबर", "mr": "पावतीसाठी मोबाइल नंबर"},
    "Operator name": {"hi": "ऑपरेटर नाम", "mr": "ऑपरेटर नाव"},
    "Recharge amount or plan": {"hi": "रिचार्ज राशि या प्लान", "mr": "रिचार्ज रक्कम किंवा प्लॅन"},
    "Receiver account or transfer details": {"hi": "प्राप्तकर्ता अकाउंट या ट्रांसफर विवरण", "mr": "प्राप्तकर्ता खाते किंवा ट्रान्सफर तपशील"},
    "Transfer amount": {"hi": "ट्रांसफर राशि", "mr": "ट्रान्सफर रक्कम"},
    "Customer mobile number": {"hi": "ग्राहक मोबाइल नंबर", "mr": "ग्राहक मोबाइल नंबर"},
    "Government ID if needed": {"hi": "जरूरत हो तो सरकारी ID", "mr": "गरज असल्यास सरकारी ID"},
    "Driving licence (optional upload)": {"hi": "ड्राइविंग लाइसेंस (वैकल्पिक अपलोड)", "mr": "ड्रायव्हिंग लायसन्स (ऐच्छिक अपलोड)"},
    "ID proof": {"hi": "ID प्रमाण", "mr": "ID पुरावा"},
    "Rental duration": {"hi": "किराया अवधि", "mr": "भाडे कालावधी"},
    "Security deposit if applicable": {"hi": "यदि लागू हो तो सिक्योरिटी डिपॉज़िट", "mr": "लागू असल्यास सिक्युरिटी डिपॉझिट"},
    "Travel distance": {"hi": "यात्रा दूरी", "mr": "प्रवास अंतर"},
    "Pickup and drop details": {"hi": "पिकअप और ड्रॉप विवरण", "mr": "पिकअप आणि ड्रॉप तपशील"},
    "Customer contact number": {"hi": "ग्राहक संपर्क नंबर", "mr": "ग्राहक संपर्क नंबर"},
    "Driver requirement if any": {"hi": "ड्राइवर आवश्यकता यदि हो", "mr": "ड्रायव्हरची गरज असल्यास"},
    "Photo and signature": {"hi": "फोटो और हस्ताक्षर", "mr": "फोटो आणि स्वाक्षरी"},
    "Education details": {"hi": "शिक्षा विवरण", "mr": "शिक्षण तपशील"},
    "Email ID and mobile number": {"hi": "ईमेल ID और मोबाइल नंबर", "mr": "ईमेल ID आणि मोबाइल नंबर"},
    "Portal fee amount": {"hi": "पोर्टल फीस राशि", "mr": "पोर्टल फी रक्कम"},
    "Upload or share the photo artwork": {"hi": "फोटो आर्टवर्क अपलोड या शेयर करें", "mr": "फोटो आर्टवर्क अपलोड किंवा शेअर करा"},
    "Mention full sheet / half sheet / small card": {"hi": "फुल शीट / हाफ शीट / छोटा कार्ड लिखें", "mr": "फुल शीट / हाफ शीट / छोटा कार्ड लिहा"},
    "Mention finish or background preference": {"hi": "फिनिश या बैकग्राउंड पसंद लिखें", "mr": "फिनिश किंवा बॅकग्राउंड पसंती लिहा"},
    "Upload a clear front-facing portrait photo": {"hi": "साफ फ्रंट-फेसिंग फोटो अपलोड करें", "mr": "स्पष्ट फ्रंट-फेसिंग फोटो अपलोड करा"},
    "Choose the photo size preset": {"hi": "फोटो साइज प्रीसेट चुनें", "mr": "फोटो साइज प्रीसेट निवडा"},
    "Choose the number of photo copies needed": {"hi": "कितनी फोटो कॉपी चाहिए चुनें", "mr": "किती फोटो कॉपी हव्यात ते निवडा"},
    "Select white or blue background if required": {"hi": "जरूरत हो तो सफेद या नीला बैकग्राउंड चुनें", "mr": "गरज असल्यास पांढरी किंवा निळी पार्श्वभूमी निवडा"},
    "Upload JPG, JPEG, or PNG image files": {"hi": "JPG, JPEG या PNG इमेज फाइलें अपलोड करें", "mr": "JPG, JPEG किंवा PNG इमेज फाइल्स अपलोड करा"},
    "Arrange images in the order you want in the PDF": {"hi": "PDF में जिस क्रम में चाहिए उस क्रम में इमेज रखें", "mr": "PDF मध्ये हव्या त्या क्रमाने इमेज ठेवा"},
    "Add any special page or naming notes if needed": {"hi": "जरूरत हो तो पेज या नामकरण नोट्स जोड़ें", "mr": "गरज असल्यास पेज किंवा नाव नोंदी जोडा"},
    "Physical document pages": {"hi": "फिजिकल डॉक्यूमेंट पेज", "mr": "फिजिकल डॉक्युमेंट पेज"},
    "Output format requirement": {"hi": "आउटपुट फॉर्मेट आवश्यकता", "mr": "आउटपुट फॉरमॅट गरज"},
    "Email / WhatsApp destination if needed": {"hi": "जरूरत हो तो ईमेल / WhatsApp डेस्टिनेशन", "mr": "गरज असल्यास ईमेल / WhatsApp ठिकाण"},
    "Source document or handwritten notes": {"hi": "सोर्स डॉक्यूमेंट या हाथ से लिखे नोट्स", "mr": "सोर्स डॉक्युमेंट किंवा हस्तलिखित नोंदी"},
    "Language requirement": {"hi": "भाषा आवश्यकता", "mr": "भाषेची गरज"},
    "Delivery format needed": {"hi": "डिलीवरी फॉर्मेट", "mr": "डिलिव्हरी फॉरमॅट"},
    "adharcard": {"hi": "आधार कार्ड", "mr": "आधार कार्ड"},
    "New PAN": {"hi": "नया पैन", "mr": "नवीन पॅन"},
    "Correction / Update": {"hi": "सुधार / अपडेट", "mr": "दुरुस्ती / अपडेट"},
    "Learner Licence (LL)": {"hi": "लर्नर लाइसेंस (LL)", "mr": "लर्नर लायसन्स (LL)"},
    "Permanent Licence (P.L.)": {"hi": "परमानेंट लाइसेंस (P.L.)", "mr": "परमनंट लायसन्स (P.L.)"},
    "Card Lamination": {"hi": "कार्ड लैमिनेशन", "mr": "कार्ड लॅमिनेशन"},
    "Laminated Download Card": {"hi": "लैमिनेटेड डाउनलोड कार्ड", "mr": "लॅमिनेटेड डाउनलोड कार्ड"},
    "A4 Lamination": {"hi": "A4 लैमिनेशन", "mr": "A4 लॅमिनेशन"},
    "Standard Form Service": {"hi": "स्टैंडर्ड फॉर्म सेवा", "mr": "स्टँडर्ड फॉर्म सेवा"},
    "Complex Form Service": {"hi": "कॉम्प्लेक्स फॉर्म सेवा", "mr": "कॉम्प्लेक्स फॉर्म सेवा"},
    "Full Photo Paper Sheet": {"hi": "फुल फोटो पेपर शीट", "mr": "फुल फोटो पेपर शीट"},
    "Half Photo Paper Sheet": {"hi": "हाफ फोटो पेपर शीट", "mr": "हाफ फोटो पेपर शीट"},
    "Small Color Point Card": {"hi": "छोटा कलर पॉइंट कार्ड", "mr": "छोटा कलर पॉइंट कार्ड"},
    "Black & White": {"hi": "ब्लैक एंड व्हाइट", "mr": "ब्लॅक अँड व्हाइट"},
    "Color": {"hi": "कलर", "mr": "कलर"},
    "Single side": {"hi": "एक तरफ", "mr": "एक बाजू"},
    "Double side": {"hi": "दोनों तरफ", "mr": "दोन्ही बाजू"},
    "Applications": {"hi": "आवेदन", "mr": "अर्ज"},
    "Requests": {"hi": "अनुरोध", "mr": "विनंत्या"},
    "Registrations": {"hi": "रजिस्ट्रेशन", "mr": "नोंदणी"},
    "Pieces": {"hi": "पीस", "mr": "पीस"},
    "Bills": {"hi": "बिल", "mr": "बिल"},
    "Recharges": {"hi": "रिचार्ज", "mr": "रिचार्ज"},
    "Transfers": {"hi": "ट्रांसफर", "mr": "ट्रान्सफर"},
    "Rental days": {"hi": "किराया दिन", "mr": "भाडे दिवस"},
    "Distance (km)": {"hi": "दूरी (किमी)", "mr": "अंतर (किमी)"},
    "Forms": {"hi": "फॉर्म", "mr": "फॉर्म"},
    "Sheets": {"hi": "शीट", "mr": "शीट"},
    "Photo copies": {"hi": "फोटो कॉपी", "mr": "फोटो कॉपी"},
    "Conversions": {"hi": "कन्वर्ज़न", "mr": "कन्वर्जन"},
    "Pages": {"hi": "पेज", "mr": "पेज"},
    "Jobs": {"hi": "काम", "mr": "कामे"},
    "Pages / copies": {"hi": "पेज / कॉपी", "mr": "पेज / कॉपी"},
    "Bill amount": {"hi": "बिल राशि", "mr": "बिल रक्कम"},
    "Transfer amount": {"hi": "ट्रांसफर राशि", "mr": "ट्रान्सफर रक्कम"},
    "Bike model / preference": {"hi": "बाइक मॉडल / पसंद", "mr": "बाईक मॉडेल / पसंती"},
    "Pickup date": {"hi": "पिकअप तारीख", "mr": "पिकअप तारीख"},
    "Return date": {"hi": "रिटर्न तारीख", "mr": "परत तारीख"},
    "Security deposit": {"hi": "सिक्योरिटी डिपॉज़िट", "mr": "सिक्युरिटी डिपॉझिट"},
    "Pickup location": {"hi": "पिकअप लोकेशन", "mr": "पिकअप ठिकाण"},
    "Drop location": {"hi": "ड्रॉप लोकेशन", "mr": "ड्रॉप ठिकाण"},
    "Travel date": {"hi": "यात्रा तारीख", "mr": "प्रवास तारीख"},
    "Driver needed": {"hi": "ड्राइवर चाहिए", "mr": "ड्रायव्हर हवा आहे"},
    "No": {"hi": "नहीं", "mr": "नाही"},
    "Yes": {"hi": "हाँ", "mr": "होय"},
}


def _slab_price(amount: float, slab_size: float, slab_rate: float) -> float:
    return slab_price(amount, slab_size, slab_rate)


def _multiplier_price(units: float, unit_rate: float) -> float:
    return multiplier_price(units, unit_rate)


def _t(language: str, text: str) -> str:
    if text in UPLOAD_TRANSLATIONS:
        return UPLOAD_TRANSLATIONS[text].get(language, text)
    if " - " in str(text):
        head, tail = str(text).split(" - ", 1)
        return f"{_t(language, head)} - {tail}"
    return text


def _translated_service_matches(service_catalog: dict, service_names: list[str], search_term: str, language: str) -> list[str]:
    term = search_term.strip().lower()
    if not term:
        return service_names

    matched = []
    for name in service_names:
        config = service_catalog[name]
        translated_parts = [
            _t(language, name),
            _t(language, config.get("description", "")),
            *[_t(language, item) for item in config.get("checklist", [])],
            *[_t(language, item) for item in config.get("required_uploads", [])],
            *[_t(language, item) for item in config.get("optional_uploads", [])],
            *[_t(language, variant.get("label", "")) for variant in config.get("variants", [])],
        ]
        if term in " ".join(translated_parts).lower():
            matched.append(name)
    return matched


def render_upload_page(identity: dict) -> None:
    apply_upload_page_styles()
    top_bar = st.columns([4, 1])
    with top_bar[1]:
        language = st.selectbox(
            _t("en", "Language"),
            options=list(LANGUAGE_OPTIONS.keys()),
            index=list(LANGUAGE_OPTIONS.keys()).index(st.session_state.get("upload_language", "en")),
            format_func=lambda code: LANGUAGE_OPTIONS[code],
            key="upload_language_selector",
        )
    st.session_state.upload_language = language
    t = lambda text: _t(language, text)

    render_page_intro(
        t("Create Service Order"),
        t("Search the required service, check the document checklist, and create one clean order batch. Only the fields needed for the chosen service are shown."),
        eyebrow=t("Customer Desk"),
    )

    service_catalog = get_service_catalog()
    group_labels = {"all": t("All services")} | {group: t(group) for group in get_service_groups()}
    filter_cols = st.columns([0.9, 1.2])
    selected_group = filter_cols[0].selectbox(t("Service category"), list(group_labels.keys()), format_func=lambda key: group_labels[key])
    service_search = filter_cols[1].text_input(t("Search service"), placeholder=t("Search Aadhaar, PAN, photo, rental..."))
    filtered_service_names = filter_service_names(service_catalog, selected_group, service_search)
    translated_matches = _translated_service_matches(
        service_catalog,
        filter_service_names(service_catalog, selected_group, ""),
        service_search,
        language,
    )
    filtered_service_names = list(dict.fromkeys(filtered_service_names + translated_matches))

    if not filtered_service_names:
        st.warning(t("No services matched that search. Try a different keyword."))
        return

    suggestion_names = service_suggestions(service_catalog, filtered_service_names, service_search)
    if suggestion_names:
        quick_pick = st.segmented_control(
            t("Quick picks"),
            suggestion_names,
            default=st.session_state.get("selected_service_name") if st.session_state.get("selected_service_name") in suggestion_names else suggestion_names[0],
            selection_mode="single",
            format_func=lambda name: t(name),
        )
        if quick_pick:
            st.session_state.selected_service_name = quick_pick

    default_service = st.session_state.get("selected_service_name")
    default_index = filtered_service_names.index(default_service) if default_service in filtered_service_names else 0
    with st.container():
        service_name = st.selectbox(t("Service"), filtered_service_names, index=default_index, format_func=lambda name: t(name))
        st.session_state.selected_service_name = service_name
        service_config = service_catalog[service_name]
        checklist = service_config.get("checklist", [])
        required_upload_labels = service_config.get("required_uploads", [])
        optional_upload_labels = service_config.get("optional_uploads", [])
        custom_input_specs = service_config.get("custom_inputs", [])
        checklist_upload_mode = bool(checklist) and not service_config.get("upload_required", True) and not optional_upload_labels and not required_upload_labels
        optional_upload_mode = bool(optional_upload_labels)

        variant_by_name = service_variant_options(service_config)
        selected_variant_name = ""
        variant_config = {}
        if variant_by_name:
            selected_variant_name = st.selectbox(t("Service option"), list(variant_by_name.keys()), format_func=lambda name: t(name))
            variant_config = variant_by_name[selected_variant_name]

        customer_name = st.text_input(
            t("Customer name"),
            value=identity["display_name"] if identity["display_name"] != "Guest Customer" else "",
            placeholder=t("Enter customer name"),
        )
        customer_phone = st.text_input(
            t("Phone number"),
            value="",
            placeholder=t("Enter customer phone number"),
            help=t("Phone number is required for every order."),
        )
        if customer_name.strip() and not identity["is_logged_in"]:
            st.session_state.guest_name = customer_name.strip()
            identity["display_name"] = customer_name.strip()

        custom_input_values = render_custom_inputs(custom_input_specs, service_name, t=t)

        upload_required = bool(service_config.get("upload_required", True))
        extra_uploads = []
        extra_labels = []
        if required_upload_labels:
            uploaded_files, checklist_file_labels = render_document_uploader(
                required_upload_labels,
                f"required_{service_name}",
                t("Required Document Uploads"),
                t("Upload the exact documents this service needs."),
                t=t,
            )
            extra_uploads, extra_labels = render_other_documents_uploader(f"required_{service_name}", t=t)
        elif checklist_upload_mode:
            uploaded_files, checklist_file_labels = render_document_uploader(
                checklist,
                f"checklist_{service_name}",
                t("Required Document Uploads"),
                t("Upload the matching document beside each checklist item wherever it is available."),
                t=t,
            )
            extra_uploads, extra_labels = render_other_documents_uploader(f"checklist_{service_name}", t=t)
        elif optional_upload_mode:
            uploaded_files, checklist_file_labels = render_document_uploader(
                optional_upload_labels,
                f"optional_{service_name}",
                t("Optional Document Upload"),
                t("Only upload the extra supporting document if the customer wants to attach it now."),
                optional=True,
                t=t,
            )
            extra_uploads, extra_labels = render_other_documents_uploader(f"optional_{service_name}", t=t)
        else:
            uploader_label = t("Choose file(s)") if upload_required else t("Attach supporting file(s) if available")
            captured_file = None
            camera_state_key = f"generic_camera_enabled_{service_name}"
            st.markdown("<div class='required-upload-actions'>", unsafe_allow_html=True)
            uploaded_files = st.file_uploader(uploader_label, accept_multiple_files=True, type=None)
            camera_open = bool(st.session_state.get(camera_state_key, False))
            camera_label = "X" if camera_open else "📷"
            camera_help = t("Close camera") if camera_open else t("Take document photo")
            st.markdown("<div class='camera-button-cell compact-camera-action'>", unsafe_allow_html=True)
            if st.button(camera_label, key=f"{camera_state_key}_toggle", help=camera_help, type="secondary", use_container_width=True):
                st.session_state[camera_state_key] = not camera_open
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if st.session_state.get(camera_state_key, False):
                captured_file = render_live_camera(
                    t("Take document photo"),
                    key=f"generic_camera_{service_name}",
                    t=t,
                )
            if captured_file is not None:
                uploaded_files = list(uploaded_files or [])
                uploaded_files.append(
                    render_browser_camera_capture(
                        captured_file,
                        f"{service_name}_camera.jpg",
                        f"generic_camera_crop_{service_name}",
                        t=t,
                    )
                )
            checklist_file_labels = []

        if service_name == "Passport Photo Print":
            estimated_total, service_request, submission_uploads = render_photo_service_fields(service_name, service_config, uploaded_files, t=t, language=language)
        elif service_name == "JPG to PDF":
            estimated_total, service_request, submission_uploads = render_jpg_to_pdf_fields(service_name, service_config, uploaded_files, t=t)
        else:
            unit_price = float(variant_config.get("unit_price", service_config.get("unit_price", 0.0)))
            slab_amount = 0.0
            multiplier_units = 0.0
            slab_pricing = service_config.get("slab_pricing")
            multiplier_pricing = service_config.get("multiplier_pricing")

            if slab_pricing:
                slab_amount = st.number_input(
                    t(slab_pricing.get("input_label", "Amount")),
                    min_value=0.0,
                    value=float(slab_pricing.get("slab_size", 1000.0)),
                    step=100.0,
                )
                unit_price = slab_price(
                    slab_amount,
                    slab_pricing.get("slab_size", 1000.0),
                    slab_pricing.get("slab_rate", unit_price),
                )
            elif multiplier_pricing:
                multiplier_units = st.number_input(
                    t(multiplier_pricing.get("unit_label", "Units")),
                    min_value=float(multiplier_pricing.get("min_units", 1)),
                    value=float(multiplier_pricing.get("min_units", 1)),
                    step=1.0,
                )
                unit_price = multiplier_price(multiplier_units, multiplier_pricing.get("unit_rate", unit_price))

            if service_config.get("allow_custom_rate"):
                unit_price = st.number_input(
                    t("Service rate"),
                    min_value=0.0,
                    value=float(unit_price),
                    step=5.0,
                    help=t("Use this when the desk needs to override the listed rate for this job."),
                )

            st.caption(t(service_config.get("description", "")))

            quantity_label = service_config.get("quantity_label", "Copies / quantity")
            color_modes = service_config.get("color_modes", [])
            color_mode_rates = {item.get("label", ""): float(item.get("unit_price", unit_price)) for item in color_modes if item.get("label")}
            color_mode_options = list(color_mode_rates.keys())
            use_quantity_multiplier = bool(upload_required or service_config.get("pricing_mode") == "per_unit")
            order_cols = st.columns(2 if upload_required else 3)
            if use_quantity_multiplier and not upload_required:
                quantity = order_cols[0].number_input(t(quantity_label), min_value=1, max_value=500, value=1)
            else:
                quantity = 1
            urgent = False

            print_style = ""
            if service_config.get("show_print_style") and not upload_required:
                print_style = order_cols[1 if use_quantity_multiplier and not upload_required else 0].selectbox(
                    t("Print style"),
                    PRINT_STYLE_OPTIONS,
                    format_func=lambda option: t(option),
                )

            file_overrides = build_file_overrides(
                uploaded_files,
                quantity_label,
                bool(service_config.get("show_print_style")),
                color_mode_options=color_mode_options,
                t=t,
            ) if upload_required else []
            for override in file_overrides:
                override["unit_price"] = float(color_mode_rates.get(override.get("color_mode", ""), unit_price))

            notes = ""
            if service_config.get("service_group") in NOTES_SERVICE_GROUPS or service_config.get("allow_custom_rate"):
                notes = render_optional_notes(
                    "Notes",
                    f"service_{service_name}",
                    placeholder=t(service_config.get(
                        "notes_placeholder",
                        t("Add application details, page notes, payment notes, or pickup instructions."),
                    )),
                    t=t,
                )

            estimated_total = estimate_upload_total(unit_price, urgent, file_overrides, int(quantity))
            st.info(f"{t('Estimated bill')}: Rs. {estimated_total:.2f}")

            if not upload_required:
                st.caption(t("This is a desk service. A file is optional, so you can create the order even without attachments."))

            detail_lines = []
            if selected_variant_name:
                detail_lines.append(f"{t('Option')}: {t(selected_variant_name)}")
            if slab_pricing:
                detail_lines.append(f"{t('Bill amount')}: Rs. {slab_amount:.2f}")
            if multiplier_pricing:
                detail_lines.append(f"{t(multiplier_pricing.get('unit_label', 'Units'))}: {multiplier_units:.2f}")
            if print_style:
                detail_lines.append(f"{t('Print style')}: {t(print_style)}")
            if notes.strip():
                detail_lines.append(notes.strip())
            if color_mode_options and not upload_required:
                detail_lines.append(f"{t('Mode')}: {t(DEFAULT_COLOR_MODE)}")
            detail_lines.extend(summarize_custom_inputs(custom_input_values))

            service_request = {
                "service_name": service_name,
                "copies": int(quantity),
                "urgent": urgent,
                "notes": " | ".join(detail_lines),
                "unit_price": float(unit_price),
                "service_group": service_config["service_group"],
                "pricing_mode": service_config.get("pricing_mode", "per_unit"),
                "service_meta": {
                    "source": "upload_desk",
                    "service_variant": selected_variant_name,
                    "print_style": print_style,
                    "color_mode": DEFAULT_COLOR_MODE if color_mode_options else "",
                    "quantity_label": quantity_label,
                    "upload_required": upload_required,
                    "bill_amount": slab_amount if slab_pricing else 0.0,
                    "service_units": multiplier_units if multiplier_pricing else 0.0,
                    "custom_inputs": custom_input_values,
                },
                "file_overrides": file_overrides,
                "file_labels": checklist_file_labels + extra_labels,
            }
            submission_uploads = (uploaded_files or []) + extra_uploads

        if st.button(t("Create order"), use_container_width=True, type="primary"):
            if not customer_name.strip():
                st.error(t("Please enter the customer name."))
                return
            if not customer_phone.strip():
                st.error(t("Please enter the phone number."))
                return
            custom_input_error = validate_custom_inputs(custom_input_specs, custom_input_values)
            if custom_input_error:
                st.error(custom_input_error)
                return
            if upload_required and not uploaded_files:
                st.error(t("Please upload at least one supporting file for this service."))
                return
            if service_name == "Passport Photo Print" and not submission_uploads:
                st.error(t("Please upload at least one portrait photo."))
                return

            result = submit_uploads(identity, customer_name.strip(), customer_phone.strip(), submission_uploads, service_request)

            st.success(f"{t('Order created. Pickup code')}: {result['pickup_code']}")
            st.info(
                f"{len(result['upload_ids'])} {t('item(s) queued for')} {t(service_request['service_name'])}. {t('Estimated bill')}: Rs. {result['estimated_total']:.2f}"
            )
            if result["stored_file_count"]:
                st.caption(f"{result['stored_file_count']} {t('file(s) stored successfully in local Streamlit storage.')}")
            else:
                st.caption(t("This service was saved as a counter request without file storage."))
            if result["customer_tier"] == "regular":
                st.toast(t("Repeat customer detected. Added to priority follow-up."), icon="⭐")
