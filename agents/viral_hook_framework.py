"""
Viral Hook Framework & Creator Intelligence Engine.
Codifies high-retention hook formulas inspired by ViralHooks.org and reverse-engineered
from top-performing Pakistani & global accounts with 1,000+ likes and high comment velocity.

Covers all 7 Pro-Pakistan media verticals:
1. Technology & Telecom (Gadgets, PTA, 5G, Packages, ISPs)
2. Business & Finance (PSX, IMF, FBR Taxes, Startups, Crypto, Real Estate)
3. Automotive / CarBase (New Launches, Fuel Rates, On-Money, Bike Prices)
4. Sports / ProSports (Cricket Analytics, PSL, Match Records, Biomechanics)
5. Education & Scholarships (HEC, Fully-Funded Foreign Grants, Admissions)
6. Entertainment & Lifestyle / Lens (Pakistani Cinema, Dramas, Pop Culture, Celebrity)
7. Public Utility Guides (Passports, CNIC, NADRA, Driving Licenses, Digital Wallets)
"""

from typing import Dict, List, Any
import random

VIRAL_HOOK_ARCHETYPES = {
    # ── 1. The Curiosity Gap / Insider Secret ("Nobody is talking about...") ──
    "curiosity_gap": {
        "name": "Curiosity Gap & Insider Secret",
        "description": "Creates an irresistible knowledge gap that forces the viewer to stop and read.",
        "templates": [
            "Nobody is talking about the new {subject} rule taking effect this week…",
            "The {authority} quietly changed how {subject} works. Here is what it means for you:",
            "What {authority} isn't telling you about the recent {subject} update:",
            "The hidden loophole in {subject} that could save you thousands of rupees:",
            "Why 95% of people in Pakistan get {subject} completely wrong:"
        ],
        "urdu_templates": [
            "{subject} کے بارے میں سب سے بڑی غلط فہمی جس کا نقصان سب اٹھا رہے ہیں",
            "کوئی نہیں بتا رہا کہ {subject} کے نئے قوانین سے آپ پر کیا اثر پڑے گا",
            "{authority} کا خاموش فیصلہ: {subject} کے بارے میں اصل سچ سامنے آ گیا"
        ]
    },

    # ── 2. The Loss Aversion / Stop Scrolling Warning ("Stop Doing X...") ──
    "loss_aversion": {
        "name": "Loss Aversion & Critical Warning",
        "description": "Triggers immediate self-preservation instinct by warning of costly mistakes.",
        "templates": [
            "Stop {action} until you read this {subject} alert.",
            "If you own or use {subject}, do NOT make this costly mistake.",
            "3 mistakes costing Pakistanis thousands on {subject} every month.",
            "Before you pay for {subject}, check this 1 critical detail.",
            "Warning: If you get a message about {subject}, do NOT click until you read this."
        ],
        "urdu_templates": [
            "خبردار: {subject} کے حوالے سے یہ غلطی آپ کو لاکھوں کا نقصان پہنچا سکتی ہے",
            "اگر آپ {subject} کا ارادہ رکھتے ہیں تو فوراً یہ 3 باتیں نوٹ کر لیں",
            "یہ غلطی مت کریں! {subject} کے بارے میں تازہ ترین انتباہ جاری"
        ]
    },

    # ── 3. The Dream Transformation / Pain-Free Blueprint ("How to X without Y") ──
    "transformation_blueprint": {
        "name": "Actionable Blueprint & Shortcut",
        "description": "Promises high-value practical outcome with minimum hassle or cost.",
        "templates": [
            "How to get {benefit} in under {timeframe} without paying extra agents.",
            "The step-by-step roadmap to {benefit} that actually works in 2026.",
            "Tested: How to successfully apply for {subject} on your phone in 10 minutes.",
            "The exact checklist you need to unlock {benefit} this month:"
        ],
        "urdu_templates": [
            "ایجنٹوں کو پیسے دیے بغیر {subject} کا آسان ترین طریقہ (مرحلہ وار گائیڈ)",
            "گھر بیٹھے صرف 10 منٹ میں {subject} حاصل کرنے کا تصدیق شدہ طریقہ",
            "2026 کا نیا نظام: {benefit} حاصل کرنے کے آسان مراحل"
        ]
    },

    # ── 4. The Contrarian / Myth-Busting Truth ("X vs Y: Which is actually better?") ──
    "contrarian_truth": {
        "name": "Contrarian Take & Unfiltered Comparison",
        "description": "Challenges mainstream conventional wisdom with hard numbers and data.",
        "templates": [
            "Why buying {subject_a} over {subject_b} is a massive financial trap.",
            "The brutal truth about {subject} that influencers are hiding from you.",
            "We compared {subject_a} vs {subject_b} with real Pakistani data. The winner surprised us.",
            "Is {subject} actually worth your hard-earned money in 2026? The numbers say no."
        ],
        "urdu_templates": [
            "کیا واقعی {subject} پر پیسہ لگانا فائدہ مند ہے؟ حقائق اور اعداد و شمار",
            "{subject_a} بمقابلہ {subject_b}: وہ سچ جو آپ کو کوئی ڈیلر نہیں بتائے گا",
            "مارکیٹ کا سب سے بڑا دھوکہ: {subject} کی اصل قیمت جان کر آپ دنگ رہ جائیں گے"
        ]
    }
}

PRO_PAKISTAN_NICHE_MATRIX = {
    "technology_telecom": {
        "code": "tech_telecom",
        "name": "Technology & Telecom",
        "display_name": "Technology & Telecom",
        "badge": "TECH INTEL ⚡",
        "category_tag": "Telecom & 5G",
        "sub_topics": [
            "PTA tax reductions and registration policies",
            "5G spectrum rollout and auction milestones in Pakistan",
            "Best monthly internet fiber packages (Nayatel, StormFiber, PTCL Flash Fiber)",
            "Budget smartphone launches under PKR 40,000 with 120Hz displays",
            "eSIM activation guides across Jazz, Zong, Ufone and Telenor",
            "Local mobile manufacturing and export records"
        ],
        "default_stat_label": "INTERNET SPEED / TAX METRIC",
        "hook_subject": "PTA mobile taxes & 5G internet",
        "authority": "PTA & telecom operators",
        "affiliate_cta": "Compare High-Speed Fiber Plans ➔"
    },
    "business_finance": {
        "code": "business_finance",
        "name": "Business & Finance",
        "display_name": "Business & Finance",
        "badge": "FINANCE ALERT 📈",
        "category_tag": "Business & Economy",
        "sub_topics": [
            "PSX 100-index record runs and top performing dividend stocks",
            "FBR tax filing rules, late fees, and active taxpayer perks",
            "IMF bailout reviews, policy benchmarks, and interest rate cuts by SBP",
            "Pakistani tech startups raising seed capital and venture funding",
            "Roshan Digital Account updates and foreign remittances surge",
            "Gold rate movements and PKR vs USD interbank trends"
        ],
        "default_stat_label": "PSX INDEX / POLICY METRIC",
        "hook_subject": "FBR tax rules & market shifts",
        "authority": "FBR & State Bank of Pakistan",
        "affiliate_cta": "Open Verified Brokerage Account ➔"
    },
    "automotive_carbase": {
        "code": "automotive_carbase",
        "name": "Automotive (CarBase)",
        "display_name": "Automotive (CarBase)",
        "badge": "CARBASE 🚗",
        "category_tag": "Automotive News",
        "sub_topics": [
            "Petrol, diesel and CNG official fortnightly price revisions",
            "Electric vehicle (EV) launches and cheap charging infrastructure",
            "Best hybrid family sedans and crossovers in Pakistan",
            "Car booking delivery times and elimination of 'on-money' premiums",
            "Used car market inspection checklist and resale value champions",
            "New motorcycle launches and electric 2-wheeler financing schemes"
        ],
        "default_stat_label": "FUEL RATE / HORSEPOWER",
        "hook_subject": "fuel rates & car showroom prices",
        "authority": "OGRA & auto manufacturers",
        "affiliate_cta": "Check Inspected Car Listings ➔"
    },
    "sports_prosports": {
        "code": "sports_prosports",
        "name": "Sports (ProSports)",
        "display_name": "Sports (ProSports)",
        "badge": "PROSPORTS 🏏",
        "category_tag": "Sports Intelligence",
        "sub_topics": [
            "Pakistan cricket team tactical previews and squad selections",
            "PSL auction records, franchise budgets, and player retention",
            "ICC Champions Trophy fixtures, venues, and match simulations",
            "Fast bowling biomechanics: Shaheen, Naseem, and Haris Rauf",
            "Olympic sports, javelin throw records, and grassroots talent"
        ],
        "default_stat_label": "BOWLING SPEED / RUNS",
        "hook_subject": "Pakistan cricket squad selection",
        "authority": "PCB & ICC match officials",
        "affiliate_cta": "View Verified Match Tickets & Jerseys ➔"
    },
    "education_scholarships": {
        "code": "education_scholarships",
        "name": "Education & Scholarships",
        "display_name": "Education & Scholarships",
        "badge": "SCHOLARSHIP ALERT 🎓",
        "category_tag": "Education & Careers",
        "sub_topics": [
            "HEC fully-funded scholarships for Germany, UK, and Hungary",
            "Pakistani university entry tests: MDCAT, ECAT, and LAT schedules",
            "Chevening, Fulbright, and Erasmus Mundus master’s application roadmaps",
            "Top tech bootcamps in AI, Python, and cloud computing with job placement",
            "Government youth laptop schemes and digital skill stipend programs"
        ],
        "default_stat_label": "STIPEND / GRANT VALUE",
        "hook_subject": "HEC fully-funded scholarships",
        "authority": "HEC & foreign education commissions",
        "affiliate_cta": "Download Free Scholarship SOP Template ➔"
    },
    "entertainment_lens": {
        "code": "entertainment_lens",
        "name": "Entertainment & Lifestyle (Lens)",
        "display_name": "Entertainment & Lifestyle (Lens)",
        "badge": "LENS CELEBRITY 🎬",
        "category_tag": "Cinema & Pop Culture",
        "sub_topics": [
            "Box office records for Pakistani cinema releases",
            "Top trending Pakistani TV dramas and critical episode reviews",
            "Celebrity style spotlights, film festivals, and red carpets",
            "Emerging Pakistani indie musicians, Coke Studio tracks, and Spotify trends",
            "Boutique culinary reviews and heritage street food itineraries"
        ],
        "default_stat_label": "BOX OFFICE / VIEWS",
        "hook_subject": "trending Pakistani dramas & cinema",
        "authority": "Censor Board & streaming platforms",
        "affiliate_cta": "Explore Cinepax & Cinema Tickets ➔"
    },
    "public_utility_guides": {
        "code": "public_utility_guides",
        "name": "Public Utility Guides",
        "display_name": "Public Utility Guides",
        "badge": "GOVT GUIDE 📑",
        "category_tag": "Public Services",
        "sub_topics": [
            "Fast-track e-Passport application via the DGI&P online portal",
            "NADRA Smart CNIC renewal and Pak-ID biometric mobile app guide",
            "Driving license online renewal and DLIMS nationwide verification",
            "Raast P2P instant payment rails and Asaan digital bank accounts",
            "FBR asset declaration and tax return filing for non-filers"
        ],
        "default_stat_label": "PROCESSING TIME / FEE",
        "hook_subject": "passport & NADRA CNIC renewals",
        "authority": "NADRA & Passport Directorate",
        "affiliate_cta": "Access Verified Govt Portals ➔"
    }
}

class ViralHookEngine:
    @staticmethod
    def generate_hook(niche_key: str, specific_topic: str = None, lang: str = "english") -> Dict[str, str]:
        """
        Synthesizes a high-CTR attention hook using proven viral frameworks.
        """
        niche_info = PRO_PAKISTAN_NICHE_MATRIX.get(niche_key, PRO_PAKISTAN_NICHE_MATRIX["technology_telecom"])
        archetype_key = random.choice(list(VIRAL_HOOK_ARCHETYPES.keys()))
        archetype = VIRAL_HOOK_ARCHETYPES[archetype_key]

        subj = specific_topic or niche_info["hook_subject"]
        auth = niche_info["authority"]

        if lang == "urdu":
            template = random.choice(archetype["urdu_templates"])
            hook_text = template.format(subject=subj, authority=auth, benefit=subj)
        else:
            template = random.choice(archetype["templates"])
            timeframe = "48 hours"
            hook_text = template.format(
                subject=subj,
                authority=auth,
                action="buying or renewing " + subj,
                benefit="urgent " + subj,
                timeframe=timeframe,
                subject_a="the latest " + subj,
                subject_b="the imported alternative"
            )

        return {
            "archetype": archetype_key,
            "archetype_name": archetype["name"],
            "hook_text": hook_text,
            "niche_name": niche_info["name"],
            "badge": niche_info["badge"],
            "category_tag": niche_info["category_tag"]
        }

    @staticmethod
    def get_all_verticals() -> List[Dict[str, Any]]:
        return list(PRO_PAKISTAN_NICHE_MATRIX.values())
