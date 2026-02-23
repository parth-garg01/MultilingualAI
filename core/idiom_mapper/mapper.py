"""
LinguaFlow — Idiom & Cultural Mapping Engine
Detects idioms, proverbs, and culturally-specific expressions and
maps them to their equivalent in the target language.
"""

import logging
import re
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class IdiomMapper:
    """
    Rule-based idiom detection and cultural mapping engine.
    Detects idioms in source text and replaces them with
    culturally-equivalent expressions in the target language.
    """

    # Comprehensive idiom database: source_lang → {idiom → {target_lang → equivalent, meaning}}
    IDIOM_DB = {
        "en": {
            "it's raining cats and dogs": {
                "hi": "मूसलाधार बारिश हो रही है",
                "ta": "கொட்டோ கொட்டு என்று மழை பெய்கிறது",
                "meaning": "It's raining very heavily",
            },
            "break a leg": {
                "hi": "शुभकामनाएं",
                "ta": "வாழ்த்துக்கள்",
                "meaning": "Good luck",
            },
            "piece of cake": {
                "hi": "बाएं हाथ का खेल",
                "ta": "இடது கை வேலை",
                "meaning": "Very easy task",
            },
            "hit the nail on the head": {
                "hi": "बिल्कुल सही बात कही",
                "ta": "சரியாகச் சொன்னீர்கள்",
                "meaning": "To be exactly right",
            },
            "cost an arm and a leg": {
                "hi": "बहुत महंगा",
                "ta": "மிகவும் விலை அதிகம்",
                "meaning": "Very expensive",
            },
            "beat around the bush": {
                "hi": "इधर-उधर की बात करना",
                "ta": "சுற்றி வளைத்து பேசுவது",
                "meaning": "Avoid the main topic",
            },
            "once in a blue moon": {
                "hi": "कभी-कभार",
                "ta": "மிக அரிதாக",
                "meaning": "Very rarely",
            },
            "spill the beans": {
                "hi": "राज़ खोलना",
                "ta": "ரகசியத்தை வெளிப்படுத்தல்",
                "meaning": "Reveal a secret",
            },
            "the ball is in your court": {
                "hi": "अब आपकी बारी है",
                "ta": "இப்போது உங்கள் முறை",
                "meaning": "It's your turn to take action",
            },
            "bite the bullet": {
                "hi": "हिम्मत करना",
                "ta": "துணிந்து நிற்கவும்",
                "meaning": "Face a difficult situation bravely",
            },
            "burning the midnight oil": {
                "hi": "रात भर जागकर काम करना",
                "ta": "இரவு முழுவதும் விழித்து வேலை செய்வது",
                "meaning": "Working late into the night",
            },
            "under the weather": {
                "hi": "तबीयत ठीक नहीं है",
                "ta": "உடல்நிலை சரியில்லை",
                "meaning": "Feeling sick or unwell",
            },
            "a blessing in disguise": {
                "hi": "छुपा हुआ वरदान",
                "ta": "மாறுவேடத்தில் ஒரு ஆசீர்வாதம்",
                "meaning": "Something good that initially seemed bad",
            },
            "let the cat out of the bag": {
                "hi": "राज़ फाश करना",
                "ta": "ரகசியத்தை வெளியிடுவது",
                "meaning": "Accidentally reveal a secret",
            },
            "when pigs fly": {
                "hi": "जब सूरज पश्चिम से उगेगा",
                "ta": "காக்கைக்கு கொம்பு முளைத்தால்",
                "meaning": "Something that will never happen",
            },
        },
        "hi": {
            "दाल में कुछ काला है": {
                "en": "something fishy is going on",
                "ta": "ஏதோ சந்தேகமாக இருக்கிறது",
                "meaning": "Something suspicious is going on",
            },
            "नाक में दम करना": {
                "en": "to get on someone's nerves",
                "ta": "மூக்கின் மீது ஏறுவது",
                "meaning": "To annoy someone greatly",
            },
            "अंगूर खट्टे हैं": {
                "en": "sour grapes",
                "ta": "கிடைக்காத திராட்சை புளிப்பு",
                "meaning": "Pretending to not want what you can't have",
            },
            "ऊंट के मुंह में जीरा": {
                "en": "a drop in the bucket",
                "ta": "கடலில் ஒரு துளி",
                "meaning": "An insignificantly small amount",
            },
            "घर की मुर्गी दाल बराबर": {
                "en": "familiarity breeds contempt",
                "ta": "வீட்டுக் கோழி மிளகு சாமான்",
                "meaning": "We don't value what we already have",
            },
            "बंदर क्या जाने अदरक का स्वाद": {
                "en": "pearls before swine",
                "ta": "குரங்கு இஞ்சி சுவை அறியுமா",
                "meaning": "Unappreciative of something valuable",
            },
            "जैसे को तैसा": {
                "en": "tit for tat",
                "ta": "போடும் தாலிக்கு ஏற்ற சீர்",
                "meaning": "Giving someone a taste of their own medicine",
            },
            "आसमान से गिरा खजूर में अटका": {
                "en": "out of the frying pan into the fire",
                "ta": "ஆற்றில் போனது அகப்படவில்லை அலைக்கழிக்கப்பட்டது",
                "meaning": "Going from one bad situation to another",
            },
            "अपना हाथ जगन्नाथ": {
                "en": "God helps those who help themselves",
                "ta": "தன் கையே தனக்கு உதவி",
                "meaning": "Self-reliance is the best policy",
            },
            "नौ दो ग्यारह होना": {
                "en": "to run away quickly",
                "ta": "ஓட்டம் பிடிப்பது",
                "meaning": "To flee quickly",
            },
        },
        "ta": {
            "ஆறிலும் சாவு நூறிலும் சாவு": {
                "en": "might as well go all in",
                "hi": "जब डूबना ही है तो गहरे में डूबो",
                "meaning": "If the outcome is the same, take the bolder path",
            },
            "ஆடு மாடு இல்லாதவன் அடை மழையில் நனைவான்": {
                "en": "the poor always suffer the most",
                "hi": "नंगा क्या नहाएगा क्या निचोड़ेगा",
                "meaning": "Those without resources suffer disproportionately",
            },
            "கிணற்றுத் தவளை": {
                "en": "a frog in a well",
                "hi": "कुएं का मेंढक",
                "meaning": "Someone with very limited worldview",
            },
            "ஓடுகிற முயலுக்கு காதில் பிடி": {
                "en": "catch a hare by the ears",
                "hi": "भागते हुए को रोकना",
                "meaning": "Tackling an already-difficult moving problem",
            },
            "அறிவே சொத்து": {
                "en": "knowledge is wealth",
                "hi": "ज्ञान ही धन है",
                "meaning": "Knowledge is the greatest form of wealth",
            },
            "தன் வினை தன்னைச் சுடும்": {
                "en": "you reap what you sow",
                "hi": "जैसी करनी वैसी भरनी",
                "meaning": "Your own actions determine your fate",
            },
            "ஆபத்திற்கு பாவம் இல்லை": {
                "en": "desperate times call for desperate measures",
                "hi": "मजबूरी में कोई पाप नहीं",
                "meaning": "In emergencies, normal rules don't apply",
            },
        },
    }

    # Common slang/informal expressions mapping
    SLANG_MAP = {
        "en": {
            "gonna": "going to",
            "wanna": "want to",
            "gotta": "got to",
            "kinda": "kind of",
            "lemme": "let me",
        },
        "hi": {
            "yaar": "दोस्त",
            "chill maar": "आराम करो",
            "kya scene hai": "क्या हो रहा है",
        },
    }

    def __init__(self):
        logger.info(
            f"Idiom Mapper initialized with "
            f"{sum(len(v) for v in self.IDIOM_DB.values())} idioms"
        )

    def detect_idioms(self, text: str, source_lang: str) -> List[dict]:
        """
        Detect all known idioms in the input text.

        Args:
            text: Input text to scan for idioms.
            source_lang: Language code of the input text.

        Returns:
            List of detected idiom dicts with original, meaning, and position.
        """
        detected = []
        text_lower = text.lower()

        if source_lang not in self.IDIOM_DB:
            return detected

        for idiom in self.IDIOM_DB[source_lang]:
            idiom_lower = idiom.lower()
            if idiom_lower in text_lower:
                # Find position
                pos = text_lower.find(idiom_lower)
                info = self.IDIOM_DB[source_lang][idiom]
                detected.append(
                    {
                        "original": idiom,
                        "meaning": info.get("meaning", ""),
                        "position": pos,
                        "length": len(idiom),
                        "available_translations": [
                            k for k in info.keys() if k != "meaning"
                        ],
                    }
                )

        return detected

    def map_idioms(
        self, text: str, source_lang: str, target_lang: str
    ) -> Tuple[str, List[dict]]:
        """
        Detect idioms in text and replace them with cultural equivalents.

        Args:
            text: Input text.
            source_lang: Source language code.
            target_lang: Target language code.

        Returns:
            Tuple of (processed_text, list_of_idiom_mappings).
        """
        if source_lang == target_lang:
            return text, []

        idioms_found = []
        result_text = text

        if source_lang not in self.IDIOM_DB:
            return text, []

        # Sort idioms by length (longest first) to avoid partial matches
        sorted_idioms = sorted(
            self.IDIOM_DB[source_lang].keys(),
            key=len,
            reverse=True,
        )

        for idiom in sorted_idioms:
            # Case-insensitive matching
            pattern = re.compile(re.escape(idiom), re.IGNORECASE)
            match = pattern.search(result_text)

            if match:
                translations = self.IDIOM_DB[source_lang][idiom]
                if target_lang in translations:
                    replacement = translations[target_lang]
                    result_text = pattern.sub(replacement, result_text, count=1)

                    idioms_found.append(
                        {
                            "original": idiom,
                            "translated": replacement,
                            "meaning": translations.get("meaning", ""),
                            "source_lang": source_lang,
                            "target_lang": target_lang,
                        }
                    )

                    logger.info(
                        f"Idiom mapped: '{idiom}' → '{replacement}' "
                        f"({source_lang}→{target_lang})"
                    )

        return result_text, idioms_found

    def get_idiom_count(self, language: Optional[str] = None) -> int:
        """Get the number of idioms in the database."""
        if language:
            return len(self.IDIOM_DB.get(language, {}))
        return sum(len(v) for v in self.IDIOM_DB.values())

    def get_all_idioms(self, language: str) -> List[dict]:
        """Get all idioms for a specific language."""
        if language not in self.IDIOM_DB:
            return []

        return [
            {
                "idiom": idiom,
                "meaning": info.get("meaning", ""),
                "translations": {
                    k: v for k, v in info.items() if k != "meaning"
                },
            }
            for idiom, info in self.IDIOM_DB[language].items()
        ]
