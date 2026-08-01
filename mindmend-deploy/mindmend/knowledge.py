"""
knowledge.py — MindMend's response bank. Multilingual, emotion-tagged.

Each response variant is a dict:
  {"reflection": str, "follow_up": str, "emotion": str}

`emotion` drives the frontend's breathing-orb color/state. Emotions used:
  warm, gentle, concerned, encouraging, celebratory, soothing, somber, crisis

Languages: "en" (English), "hi" (Hindi), "te" (Telugu). If a language is
missing an intent, the engine falls back to English for that intent, so
partial translations are safe.

Wording philosophy: validate first, never rush to fix. Keep it long enough
to feel like a real reply, short enough to still feel like a person typing,
not an essay. One open-ended follow-up question per reply, never more.
"""

BOT_NAME = "Mira"

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "हिंदी (Hindi)",
    "te": "తెలుగు (Telugu)",
}

# ---------------------------------------------------------------------------
# Crisis handling — checked before anything else, in every language.
# ---------------------------------------------------------------------------

CRISIS_KEYWORDS = [
    "kill myself", "end my life", "want to die", "suicide", "suicidal",
    "self harm", "self-harm", "hurt myself", "cutting myself",
    "no reason to live", "better off dead", "can't go on", "cant go on",
    # Hindi (Latin + Devanagari script)
    "khud ko khatam", "marna chahta", "marna chahti", "aatmahatya",
    "आत्महत्या", "खुद को खत्म", "जीना नहीं चाहता", "जीना नहीं चाहती",
    # Telugu (Latin + Telugu script)
    "chachipothanu", "atmahatya", "ఆత్మహత్య", "చచ్చిపోవాలని",
]

CRISIS_RESPONSE = {
    "en": (
        "I'm really glad you told me this, and I want you to know you don't have "
        "to carry it alone. What you're feeling matters, and there are people who "
        "can help right now, not just a chatbot.\n\n"
        "If you're in India, you can reach:\n"
        "• Kiran Mental Health Helpline: 1800-599-0019 (24/7, toll-free)\n"
        "• iCall: 9152987821\n"
        "• Vandrevala Foundation: 1860-2662-345\n\n"
        "If you're outside India, please look up a local crisis line or go to "
        "your nearest emergency room. Is there someone you trust — a friend, "
        "family member, or counselor — you could reach out to right now?"
    ),
    "hi": (
        "मुझे सच में अच्छा लगा कि आपने यह मुझे बताया, और मैं चाहती हूँ कि आप जानें कि आपको यह "
        "अकेले नहीं सहना है। आप जो महसूस कर रहे हैं वह मायने रखता है, और अभी मदद करने वाले लोग "
        "मौजूद हैं, सिर्फ एक चैटबॉट नहीं।\n\n"
        "अगर आप भारत में हैं, तो यहाँ संपर्क करें:\n"
        "• किरण मेंटल हेल्थ हेल्पलाइन: 1800-599-0019 (24/7, टोल-फ्री)\n"
        "• iCall: 9152987821\n"
        "• वंद्रेवाला फाउंडेशन: 1860-2662-345\n\n"
        "क्या कोई ऐसा व्यक्ति है जिस पर आप भरोसा करते हैं — कोई दोस्त, परिवार का सदस्य, "
        "या काउंसलर — जिससे आप अभी बात कर सकें?"
    ),
    "te": (
        "మీరు ఇది నాకు చెప్పినందుకు నాకు నిజంగా సంతోషంగా ఉంది, మరియు మీరు దీన్ని ఒంటరిగా "
        "మోయాల్సిన అవసరం లేదని మీరు తెలుసుకోవాలని నేను కోరుకుంటున్నాను. మీరు అనుభవిస్తున్నది "
        "ముఖ్యమైనది, మరియు ఇప్పుడు సహాయం చేయగల వ్యక్తులు ఉన్నారు, కేవలం ఒక చాట్‌బాట్ మాత్రమే కాదు.\n\n"
        "మీరు భారతదేశంలో ఉంటే, వీటిని సంప్రదించవచ్చు:\n"
        "• కిరణ్ మెంటల్ హెల్త్ హెల్ప్‌లైన్: 1800-599-0019 (24/7, టోల్-ఫ్రీ)\n"
        "• iCall: 9152987821\n"
        "• వంద్రేవాలా ఫౌండేషన్: 1860-2662-345\n\n"
        "మీరు నమ్మే ఎవరైనా — స్నేహితుడు, కుటుంబ సభ్యుడు, లేదా కౌన్సెలర్ — ఇప్పుడు మీరు "
        "సంప్రదించగలరా?"
    ),
}

# ---------------------------------------------------------------------------
# Intent keyword map (kept flat across languages — simple substring match).
# ---------------------------------------------------------------------------

INTENT_KEYWORDS = {
    "greeting": ["hi", "hello", "hey", "yo", "good morning", "good evening", "hola",
                 "namaste", "namaskaram", "vanakkam"],
    "goodbye": ["bye", "goodbye", "see you", "talk later", "gtg", "got to go", "logging off",
                "phir milte", "veltha"],
    "gratitude": ["thank you", "thanks", "appreciate it", "grateful", "shukriya", "dhanyavad", "chala thanks"],
    "anxiety": ["anxious", "anxiety", "panic", "nervous", "overthinking", "racing thoughts",
                "worried", "worry", "on edge", "can't breathe", "cant breathe",
                "ghabrahat", "tension", "batuku"],
    "academic_stress": ["exam", "exams", "assignment", "deadline", "grades", "semester",
                         "project submission", "viva", "backlog", "study pressure", "gpa",
                         "padhai", "chaduvu", "marks"],
    "sadness": ["sad", "down", "depressed", "empty", "hopeless", "crying", "cry",
                "numb", "low", "unmotivated", "worthless", "udaas", "badhaga"],
    "loneliness": ["lonely", "alone", "no friends", "isolated", "left out", "nobody understands",
                   "akela", "ontari"],
    "anger": ["angry", "furious", "frustrated", "irritated", "pissed off", "mad at", "gussa", "kopam"],
    "sleep": ["can't sleep", "cant sleep", "insomnia", "tired", "exhausted", "no energy",
              "overslept", "sleep schedule", "neend nahi", "nidra radu"],
    "positive": ["good day", "feeling good", "happy", "proud of myself", "great news", "excited",
                 "khush", "santosham"],
    "smalltalk": ["how are you", "what are you", "who are you", "what can you do", "tum kaun ho", "nuvvu evaru"],
}

# ---------------------------------------------------------------------------
# Response bank per language. Each intent: list of variants.
# ---------------------------------------------------------------------------

RESPONSES = {
    "en": {
        "greeting": [
            {"reflection": f"Hey, really good to see you. I'm {BOT_NAME} — think of this as a quiet "
                            "corner where you don't have to perform or explain yourself, you can just talk.",
             "follow_up": "What's actually going on with you today?", "emotion": "warm"},
            {"reflection": "Hi there. I'm glad you opened this instead of just sitting with whatever's "
                            "on your mind by yourself.",
             "follow_up": "How's your day been — not the polite version, the real one?", "emotion": "gentle"},
        ],
        "goodbye": [
            {"reflection": "Take care of yourself out there, okay? You did something good just by "
                            "showing up and talking today.",
             "follow_up": "Come back whenever you need to — I'll be right here.", "emotion": "warm"},
        ],
        "gratitude": [
            {"reflection": "You really don't need to thank me, but it means something that you did.",
             "follow_up": "Is there anything else sitting on your mind before we wrap up?", "emotion": "warm"},
        ],
        "anxiety": [
            {"reflection": "That racing, on-edge feeling is genuinely exhausting, and it makes complete "
                            "sense that it's hard to think about anything else right now. Your body isn't "
                            "overreacting — it's just trying to protect you from something that feels big.",
             "follow_up": "Can you tell me what the loudest worry in your head sounds like right now?",
             "emotion": "concerned"},
            {"reflection": "Anxiety has this way of making everything feel urgent and enormous, even when "
                            "part of you already knows it might not be. That gap between what you feel and "
                            "what you know is a really uncomfortable place to sit in.",
             "follow_up": "If it helps, we could try a quick grounding exercise together — or would you "
                           "rather just talk it out first?", "emotion": "soothing"},
        ],
        "academic_stress": [
            {"reflection": "Deadlines and grades have this way of making it feel like your entire worth is "
                            "riding on one submission, and that pressure is real, not dramatic. It's exhausting "
                            "to carry, especially when it feels like everyone else has it figured out.",
             "follow_up": "What's the one part of this that feels heaviest right now?", "emotion": "concerned"},
            {"reflection": "That kind of nonstop academic pressure builds up quietly until suddenly it's all "
                            "you can think about. You're allowed to find this hard, even if other people seem "
                            "to handle it fine.",
             "follow_up": "Have you managed any real breaks lately, or has it just been go-go-go?", "emotion": "gentle"},
        ],
        "sadness": [
            {"reflection": "I hear you, and that heaviness is real — you don't have to explain it away or "
                            "justify it to me or to anyone. Sometimes sadness doesn't need a clean reason to "
                            "be valid.",
             "follow_up": "How long has it been sitting with you like this?", "emotion": "somber"},
            {"reflection": "Feeling numb or low like this can be its own quiet kind of exhausting, even when "
                            "nothing dramatic is happening on the outside.",
             "follow_up": "Is there anything at all — even something small — that's felt okay today?", "emotion": "somber"},
        ],
        "loneliness": [
            {"reflection": "Feeling like no one really gets it is such a heavy, isolating kind of pain, and "
                            "it's especially hard when it happens in a place that's supposed to feel social, "
                            "like college. You're not broken for feeling this way.",
             "follow_up": "When did you start feeling this disconnected from people around you?", "emotion": "somber"},
        ],
        "anger": [
            {"reflection": "That frustration sounds like it's been building for a while, not just something "
                            "that came out of nowhere today. Anger usually shows up when something you actually "
                            "care about got crossed or ignored.",
             "follow_up": "What actually set it off today?", "emotion": "concerned"},
        ],
        "sleep": [
            {"reflection": "Running on no sleep makes literally everything harder — your patience, your focus, "
                            "even how loud your own thoughts feel. It's not just tiredness, it wears down your "
                            "whole capacity to cope.",
             "follow_up": "Is it that your mind won't switch off, or has your schedule just gone sideways?",
             "emotion": "gentle"},
        ],
        "positive": [
            {"reflection": "That's genuinely great to hear, and I'm really glad today's treating you well. "
                            "Good days deserve to be noticed too, not just the hard ones.",
             "follow_up": "What's been the best part of it so far?", "emotion": "celebratory"},
        ],
        "smalltalk": [
            {"reflection": f"I'm {BOT_NAME}, a peer-support companion built into MindMend for students. "
                            "I'm not a therapist, and I won't pretend to be one, but I'm genuinely here to "
                            "listen and help you think things through, at whatever hour you need it.",
             "follow_up": "So — what actually brought you here today?", "emotion": "warm"},
        ],
        "general_support": [
            {"reflection": "I'm listening, properly. Whatever you're about to say, take your time with it.",
             "follow_up": "What's been the hardest part of it?", "emotion": "gentle"},
            {"reflection": "That sounds like a genuinely lot to be carrying around, especially if you've "
                            "been holding it in for a while.",
             "follow_up": "How long has this been going on?", "emotion": "concerned"},
        ],
    },
    "hi": {
        "greeting": [
            {"reflection": f"हाय, आपको देखकर अच्छा लगा। मैं {BOT_NAME} हूँ — इसे एक शांत कोना समझिए जहाँ आपको "
                            "खुद को साबित करने या सफाई देने की ज़रूरत नहीं है, बस बात कीजिए।",
             "follow_up": "आज असल में आपके मन में क्या चल रहा है?", "emotion": "warm"},
        ],
        "goodbye": [
            {"reflection": "अपना ख्याल रखिएगा, ठीक है? आज बात करने और यहाँ आने भर से आपने अच्छा किया।",
             "follow_up": "जब भी ज़रूरत हो वापस आइए — मैं यहीं रहूँगी।", "emotion": "warm"},
        ],
        "gratitude": [
            {"reflection": "आपको धन्यवाद कहने की ज़रूरत नहीं है, पर आपने कहा, इसका मतलब है।",
             "follow_up": "क्या कुछ और है जो अभी आपके मन में है?", "emotion": "warm"},
        ],
        "anxiety": [
            {"reflection": "यह बेचैनी, यह घबराहट सच में थका देने वाली होती है, और यह पूरी तरह समझ में आता है "
                            "कि अभी किसी और चीज़ के बारे में सोचना मुश्किल है। आपका शरीर ज़्यादा प्रतिक्रिया नहीं दे "
                            "रहा — वह सिर्फ किसी बड़ी चीज़ से आपको बचाने की कोशिश कर रहा है।",
             "follow_up": "अभी आपके दिमाग में सबसे तेज़ आवाज़ में कौन सी चिंता चल रही है?", "emotion": "concerned"},
        ],
        "academic_stress": [
            {"reflection": "डेडलाइन और मार्क्स कभी-कभी ऐसा एहसास दिलाते हैं जैसे आपकी पूरी कीमत एक सबमिशन पर "
                            "टिकी है, और यह दबाव असली है, बनावटी नहीं। यह थका देने वाला होता है, खासकर जब लगे "
                            "कि बाकी सबने सब कुछ संभाल लिया है।",
             "follow_up": "इसमें सबसे भारी हिस्सा अभी क्या लग रहा है?", "emotion": "concerned"},
        ],
        "sadness": [
            {"reflection": "मैं सुन रही हूँ, और यह भारीपन असली है — इसे मुझे या किसी को भी समझाने की ज़रूरत "
                            "नहीं है। कभी-कभी उदासी को सही होने के लिए किसी साफ वजह की ज़रूरत नहीं होती।",
             "follow_up": "यह कब से आपके साथ ऐसे ही बना हुआ है?", "emotion": "somber"},
        ],
        "loneliness": [
            {"reflection": "ऐसा महसूस होना कि कोई सच में समझता नहीं है, बहुत भारी और अकेला कर देने वाला दर्द "
                            "है, खासकर तब जब यह कॉलेज जैसी जगह में हो जो सोशल होनी चाहिए।",
             "follow_up": "आपको लोगों से यह दूरी कब से महसूस होने लगी?", "emotion": "somber"},
        ],
        "anger": [
            {"reflection": "यह गुस्सा लग रहा है काफी समय से जमा हो रहा था, अचानक नहीं आया। गुस्सा अक्सर तब "
                            "आता है जब कोई ऐसी चीज़ जो आपको सच में मायने रखती है, नज़रअंदाज़ हो जाती है।",
             "follow_up": "आज असल में इसे किस बात ने भड़काया?", "emotion": "concerned"},
        ],
        "sleep": [
            {"reflection": "नींद पूरी न होने से सच में हर चीज़ मुश्किल लगने लगती है — धैर्य, फोकस, यहाँ तक कि "
                            "अपने खुद के विचार भी ज़्यादा तेज़ लगने लगते हैं।",
             "follow_up": "क्या दिमाग शांत नहीं हो रहा, या नींद का समय ही गड़बड़ हो गया है?", "emotion": "gentle"},
        ],
        "positive": [
            {"reflection": "यह सुनकर सच में बहुत अच्छा लगा, मुझे खुशी है कि आज का दिन अच्छा जा रहा है।",
             "follow_up": "अब तक इसका सबसे अच्छा हिस्सा क्या रहा?", "emotion": "celebratory"},
        ],
        "smalltalk": [
            {"reflection": f"मैं {BOT_NAME} हूँ, MindMend में छात्रों के लिए एक पीयर-सपोर्ट साथी। मैं थेरेपिस्ट "
                            "नहीं हूँ, और वैसा दिखावा भी नहीं करूँगी, पर मैं सुनने और सोचने में साथ देने के लिए यहाँ हूँ।",
             "follow_up": "तो — आज आप यहाँ असल में किस वजह से आए?", "emotion": "warm"},
        ],
        "general_support": [
            {"reflection": "मैं ध्यान से सुन रही हूँ। आप जो भी कहना चाहें, अपने समय से कहिए।",
             "follow_up": "इसमें सबसे मुश्किल हिस्सा क्या रहा है?", "emotion": "gentle"},
        ],
    },
    "te": {
        "greeting": [
            {"reflection": f"హాయ్, మిమ్మల్ని చూసి చాలా సంతోషంగా ఉంది. నేను {BOT_NAME} — దీన్ని మీరు ఏమీ "
                            "నిరూపించుకోవాల్సిన అవసరం లేని ప్రశాంతమైన మూలగా అనుకోండి, కేవలం మాట్లాడండి.",
             "follow_up": "ఈరోజు నిజంగా మీ మనసులో ఏం జరుగుతోంది?", "emotion": "warm"},
        ],
        "goodbye": [
            {"reflection": "మీ జాగ్రత్తలో మీరు ఉండండి, సరేనా? ఈరోజు వచ్చి మాట్లాడినందుకే మీరు మంచి పని చేశారు.",
             "follow_up": "మీకు అవసరమైనప్పుడు మళ్ళీ రండి — నేను ఇక్కడే ఉంటాను.", "emotion": "warm"},
        ],
        "gratitude": [
            {"reflection": "మీరు నాకు కృతజ్ఞతలు చెప్పాల్సిన అవసరం లేదు, కానీ మీరు చెప్పడం అర్థవంతంగా ఉంది.",
             "follow_up": "ఇంకా ఏదైనా మీ మనసులో ఉందా?", "emotion": "warm"},
        ],
        "anxiety": [
            {"reflection": "ఆ ఆందోళన, ఆ కంగారు నిజంగా అలసిపోయేలా చేస్తుంది, మరియు ఇప్పుడు వేరే దేని గురించి "
                            "ఆలోచించడం కష్టంగా ఉండటం పూర్తిగా అర్థమయ్యే విషయమే. మీ శరీరం అతిగా స్పందించడం లేదు — "
                            "అది మిమ్మల్ని ఏదో పెద్దదిగా అనిపించే దాని నుండి కాపాడటానికి ప్రయత్నిస్తోంది.",
             "follow_up": "ఇప్పుడు మీ మనసులో అత్యంత బలంగా ఉన్న ఆందోళన ఏమిటి?", "emotion": "concerned"},
        ],
        "academic_stress": [
            {"reflection": "డెడ్‌లైన్‌లు మరియు మార్కులు కొన్నిసార్లు మీ మొత్తం విలువ ఒక సమర్పణపైనే ఆధారపడి "
                            "ఉన్నట్టు అనిపించేలా చేస్తాయి, మరియు ఆ ఒత్తిడి నిజమైనదే, అతిశయోక్తి కాదు.",
             "follow_up": "దీంట్లో ఇప్పుడు అత్యంత భారంగా అనిపిస్తున్న భాగం ఏమిటి?", "emotion": "concerned"},
        ],
        "sadness": [
            {"reflection": "నేను వింటున్నాను, మరియు ఆ బరువు నిజమైనది — దాన్ని నాకు లేదా ఎవరికైనా వివరించాల్సిన "
                            "అవసరం లేదు. కొన్నిసార్లు విచారానికి సరైనదిగా ఉండటానికి స్పష్టమైన కారణం అవసరం లేదు.",
             "follow_up": "ఇది మీతో ఎంతకాలంగా ఇలా ఉంది?", "emotion": "somber"},
        ],
        "loneliness": [
            {"reflection": "ఎవరూ నిజంగా అర్థం చేసుకోవడం లేదని అనిపించడం చాలా బరువైన, ఒంటరితనం కలిగించే బాధ, "
                            "ముఖ్యంగా కాలేజీ లాంటి సామాజికంగా ఉండాల్సిన చోట ఇలా అనిపించినప్పుడు.",
             "follow_up": "మీకు చుట్టూ ఉన్న వారి నుండి ఈ దూరం ఎప్పటి నుండి అనిపిస్తోంది?", "emotion": "somber"},
        ],
        "anger": [
            {"reflection": "ఈ కోపం కొంతకాలంగా పేరుకుపోతున్నట్టు అనిపిస్తోంది, ఈరోజు అకస్మాత్తుగా వచ్చింది కాదు.",
             "follow_up": "ఈరోజు దీన్ని నిజంగా ఏది రేకెత్తించింది?", "emotion": "concerned"},
        ],
        "sleep": [
            {"reflection": "నిద్ర లేకుండా ఉండటం నిజంగా ప్రతిదాన్ని కష్టతరం చేస్తుంది — ఓర్పు, దృష్టి, మీ సొంత "
                            "ఆలోచనలు కూడా చాలా బిగ్గరగా అనిపిస్తాయి.",
             "follow_up": "మీ మనసు నిద్రపోనివ్వడం లేదా, లేదా మీ నిద్ర సమయమే మారిపోయిందా?", "emotion": "gentle"},
        ],
        "positive": [
            {"reflection": "అది వినడానికి నిజంగా చాలా సంతోషంగా ఉంది, ఈరోజు మీకు బాగా జరుగుతున్నందుకు సంతోషం.",
             "follow_up": "ఇప్పటివరకు దీంట్లో అత్యుత్తమ భాగం ఏమిటి?", "emotion": "celebratory"},
        ],
        "smalltalk": [
            {"reflection": f"నేను {BOT_NAME}, MindMend లో విద్యార్థుల కోసం ఉన్న పీర్-సపోర్ట్ తోడు. నేను "
                            "థెరపిస్ట్ కాదు, అలా నటించను కూడా, కానీ వినడానికి మరియు ఆలోచించడంలో సహాయం చేయడానికి "
                            "నిజంగా ఇక్కడ ఉన్నాను.",
             "follow_up": "కాబట్టి — ఈరోజు మిమ్మల్ని ఇక్కడికి నిజంగా ఏది తీసుకువచ్చింది?", "emotion": "warm"},
        ],
        "general_support": [
            {"reflection": "నేను జాగ్రత్తగా వింటున్నాను. మీరు చెప్పాలనుకున్నది, మీ సమయం తీసుకుని చెప్పండి.",
             "follow_up": "దీంట్లో అత్యంత కష్టమైన భాగం ఏమిటి?", "emotion": "gentle"},
        ],
    },
}

GROUNDING_TECHNIQUES = {
    "en": [
        "Try the 5-4-3-2-1 method: name 5 things you can see, 4 you can touch, 3 you can "
        "hear, 2 you can smell, and 1 you can taste. It pulls your mind back into the present.",
        "Box breathing can help: breathe in for 4 counts, hold for 4, breathe out for 4, hold "
        "for 4. Repeat it a few times — the orb above is actually pacing that same rhythm.",
        "Sometimes writing the thought down exactly as it sounds in your head, no editing, "
        "takes some of its power away. Want to try that here?",
    ],
    "hi": [
        "5-4-3-2-1 तरीका आज़माइए: 5 चीज़ें जो आप देख सकते हैं, 4 जो छू सकते हैं, 3 जो सुन सकते हैं, "
        "2 जो सूंघ सकते हैं, और 1 जो चख सकते हैं — इन्हें नाम दीजिए। यह आपको वर्तमान में वापस लाता है।",
        "बॉक्स ब्रीदिंग मदद कर सकती है: 4 गिनती तक सांस लें, 4 तक रोकें, 4 तक छोड़ें, 4 तक रोकें। "
        "ऊपर वाला ऑर्ब असल में इसी लय में चल रहा है।",
    ],
    "te": [
        "5-4-3-2-1 పద్ధతిని ప్రయత్నించండి: మీరు చూడగలిగే 5, తాకగలిగే 4, వినగలిగే 3, వాసన చూడగలిగే 2, "
        "రుచి చూడగలిగే 1 వస్తువులను పేర్కొనండి. ఇది మిమ్మల్ని ప్రస్తుత క్షణంలోకి తీసుకువస్తుంది.",
        "బాక్స్ బ్రీతింగ్ సహాయపడుతుంది: 4 లెక్కల వరకు పీల్చండి, 4 వరకు ఆపండి, 4 వరకు వదలండి, 4 వరకు ఆపండి. "
        "పైన ఉన్న ఆర్బ్ నిజానికి అదే లయలో కదులుతోంది.",
    ],
}
