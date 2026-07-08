"""
Knowledge base for the Pregnancy AI Assistant.

Each entry is a small "document" the retrieval logic in `assistant.py`
can search over:

    {
        "id":       unique slug, used for debugging/logging
        "category": grouping shown to the user (Nutrition, Medical, ...)
        "keywords": phrases / synonyms a user might type — this is what
                    gets matched against, so the more natural variations
                    listed here, the better the assistant understands
                    different phrasings of the same question.
        "answer":   the friendly, medically-responsible answer.
        "urgent":   True for topics that should always nudge the user
                    towards contacting a healthcare provider promptly.
    }

This acts as a lightweight retrieval corpus (a simple, dependency-free
stand-in for a full RAG vector store) — `assistant.py` scores the
user's question against every `keywords` entry and returns the best
match rather than relying on a long if/else chain.
"""

DISCLAIMER = (
    "\n\n_This is general educational information and not a medical "
    "diagnosis. Please consult your healthcare provider for advice "
    "specific to your pregnancy._"
)

KNOWLEDGE_BASE = [
    # ------------------------------------------------------------------
    # Pregnancy basics
    # ------------------------------------------------------------------
    {
        "id": "morning_sickness",
        "category": "Pregnancy",
        "keywords": [
            "morning sickness", "nausea", "is nausea normal", "feeling sick",
            "throwing up", "vomiting in pregnancy", "queasy",
        ],
        "answer": (
            "Morning sickness (nausea, sometimes with vomiting) is very common, "
            "especially in the first trimester. It usually eases by weeks 12–14. "
            "Eating small, frequent meals, ginger tea, and avoiding strong smells "
            "can help.\n\n🚨 See a doctor if you can't keep fluids down for over "
            "24 hours, or if vomiting is severe (this can be a sign of "
            "hyperemesis gravidarum)."
        ),
    },
    {
        "id": "fatigue",
        "category": "Pregnancy",
        "keywords": ["fatigue", "tired", "exhausted", "low energy", "sleepy all the time"],
        "answer": (
            "Fatigue is extremely common, particularly in the first and third "
            "trimesters, due to hormonal changes and your body's increased "
            "workload. Rest when you can, keep meals balanced, and consider "
            "light activity, which can actually boost energy.\n\n🚨 Mention "
            "persistent, severe fatigue to your provider — it can sometimes "
            "point to anemia."
        ),
    },
    {
        "id": "headaches",
        "category": "Pregnancy",
        "keywords": ["headache", "is headache normal", "head pain", "migraine"],
        "answer": (
            "Mild headaches are common during pregnancy due to hormonal shifts, "
            "dehydration, or tension. Rest, hydration, and a warm or cool "
            "compress often help.\n\n🚨 Seek medical attention if a headache is "
            "severe, sudden, persistent, or comes with blurred vision or "
            "swelling — these can be signs of preeclampsia."
        ),
    },
    {
        "id": "mood_swings",
        "category": "Pregnancy",
        "keywords": [
            "mood swings", "emotional", "feeling anxious", "crying a lot",
            "irritable", "mood changes",
        ],
        "answer": (
            "Mood swings are common thanks to shifting hormones, physical "
            "changes, and the emotional weight of pregnancy itself. Sleep, "
            "gentle movement, and talking to someone you trust all help.\n\n"
            "🚨 If sadness, anxiety, or hopelessness last more than two weeks "
            "or feel overwhelming, please reach out to your healthcare "
            "provider — support is available."
        ),
    },
    {
        "id": "braxton_hicks",
        "category": "Pregnancy",
        "keywords": [
            "braxton hicks", "practice contractions", "tightening belly",
            "false labor",
        ],
        "answer": (
            "Braxton Hicks contractions are irregular, usually painless "
            "'practice' tightenings that can start in the second trimester. "
            "They're normal and typically ease with rest or hydration.\n\n"
            "🚨 If contractions become regular, painful, or increase in "
            "frequency before 37 weeks, contact your provider — this could be "
            "preterm labor."
        ),
    },
    {
        "id": "back_pain",
        "category": "Pregnancy",
        "keywords": ["back pain", "backache", "lower back pain"],
        "answer": (
            "Back pain is common as your center of gravity shifts and "
            "ligaments loosen. Good posture, supportive shoes, prenatal "
            "stretches, and sleeping on your side with a pillow between your "
            "knees can help.\n\n🚨 Seek care for sudden, severe back pain, "
            "especially with fever or bleeding."
        ),
    },
    {
        "id": "swollen_feet",
        "category": "Pregnancy",
        "keywords": [
            "swollen feet", "swelling", "swollen ankles", "puffy feet", "edema",
        ],
        "answer": (
            "Mild swelling in the feet and ankles is common, especially later "
            "in pregnancy, due to fluid retention. Elevating your feet, "
            "staying hydrated, and avoiding long periods of standing can "
            "help.\n\n🚨 Sudden or severe swelling — especially in the face "
            "and hands — combined with headache or vision changes can signal "
            "preeclampsia and needs prompt medical attention."
        ),
    },
    {
        "id": "sleeping_positions",
        "category": "Pregnancy",
        "keywords": [
            "sleeping position", "how should i sleep", "sleep on my back",
            "best sleeping position", "sleeping on side",
        ],
        "answer": (
            "From the second trimester onward, sleeping on your left side is "
            "generally recommended to improve blood flow to the baby and your "
            "organs. A pregnancy pillow between the knees or behind the back "
            "can add comfort.\n\n🚨 If you struggle to find a comfortable "
            "position or have trouble breathing while lying down, mention it "
            "to your provider."
        ),
    },
    {
        "id": "water_intake",
        "category": "Pregnancy",
        "keywords": [
            "water intake", "how much water", "hydration", "drink enough water",
        ],
        "answer": (
            "Most guidelines recommend around 8–10 glasses (roughly 2–2.5 "
            "liters) of water a day during pregnancy, more if you're active "
            "or it's hot. Good hydration supports amniotic fluid levels and "
            "helps prevent constipation and swelling."
            + DISCLAIMER
        ),
    },
    # ------------------------------------------------------------------
    # Nutrition
    # ------------------------------------------------------------------
    {
        "id": "nutrition",
        "category": "Nutrition",
        "keywords": [
            "what should i eat", "nutrition", "diet", "healthy eating",
            "food to eat", "pregnancy diet",
        ],
        "answer": (
            "A balanced pregnancy diet generally includes:\n\n"
            "• Fruits and vegetables\n"
            "• Whole grains\n"
            "• Lean protein\n"
            "• Dairy or calcium-rich alternatives\n"
            "• Plenty of water\n\n"
            "Try to limit processed foods, excess sugar, and raw or "
            "undercooked meat/fish."
            + DISCLAIMER
        ),
    },
    {
        "id": "weight_gain",
        "category": "Nutrition",
        "keywords": [
            "weight gain", "how much weight should i gain", "gaining too much weight",
        ],
        "answer": (
            "Healthy weight gain varies by your pre-pregnancy BMI, but a "
            "common general guideline is about 11–16 kg (25–35 lb) for a "
            "typical single pregnancy, gained gradually rather than all at "
            "once.\n\n🚨 Your provider can give you a target tailored to your "
            "starting weight and health history."
        ),
    },
    {
        "id": "prenatal_vitamins",
        "category": "Nutrition",
        "keywords": [
            "prenatal vitamins", "what vitamins should i take", "supplements",
            "vitamins during pregnancy",
        ],
        "answer": (
            "Prenatal vitamins commonly include:\n\n"
            "• Folic acid\n"
            "• Iron\n"
            "• Calcium\n"
            "• Vitamin D\n\n"
            "Only take supplements recommended or prescribed by your "
            "healthcare provider, and mention any others you're already "
            "taking."
            + DISCLAIMER
        ),
    },
    {
        "id": "folic_acid",
        "category": "Nutrition",
        "keywords": ["folic acid", "folate"],
        "answer": (
            "Folic acid helps prevent neural tube defects and supports early "
            "fetal development. It's typically recommended before conception "
            "and through at least the first trimester, often continued as "
            "part of a prenatal vitamin throughout pregnancy."
            + DISCLAIMER
        ),
    },
    {
        "id": "iron_deficiency",
        "category": "Nutrition",
        "keywords": [
            "iron deficiency", "low iron", "anemia diet", "iron rich foods",
        ],
        "answer": (
            "Iron needs increase during pregnancy to support increased blood "
            "volume. Iron-rich foods include lean red meat, beans, leafy "
            "greens, and fortified cereals — pairing them with vitamin C can "
            "improve absorption.\n\n🚨 If you feel unusually tired, dizzy, or "
            "short of breath, ask your provider about checking for anemia."
        ),
    },
    {
        "id": "calcium",
        "category": "Nutrition",
        "keywords": ["calcium", "calcium intake", "bone health pregnancy"],
        "answer": (
            "Calcium supports your baby's developing bones and teeth, and "
            "helps protect your own bone density. Good sources include dairy "
            "products, fortified plant milks, tofu, and leafy greens."
            + DISCLAIMER
        ),
    },
    # ------------------------------------------------------------------
    # Exercise
    # ------------------------------------------------------------------
    {
        "id": "exercise",
        "category": "Lifestyle",
        "keywords": [
            "can i exercise", "exercise", "working out", "prenatal yoga",
            "physical activity",
        ],
        "answer": (
            "Light to moderate exercise — such as walking, swimming, or "
            "prenatal yoga — is generally safe and beneficial for most "
            "pregnancies, helping with energy, mood, and sleep.\n\n🚨 Always "
            "check with your healthcare provider before starting or "
            "continuing an exercise program, especially if you have "
            "pregnancy complications."
        ),
    },
    # ------------------------------------------------------------------
    # Baby development
    # ------------------------------------------------------------------
    {
        "id": "baby_development",
        "category": "Baby Development",
        "keywords": [
            "baby development", "week by week", "how is my baby growing",
            "fetal development",
        ],
        "answer": (
            "Your baby develops rapidly week by week — organs form in the "
            "first trimester, movement and senses develop in the second, and "
            "rapid weight gain happens in the third. Check the Pregnancy "
            "Tracker page for a stage-by-stage breakdown matched to your "
            "current week."
            + DISCLAIMER
        ),
    },
    {
        "id": "fetal_movement",
        "category": "Baby Development",
        "keywords": [
            "fetal movement", "baby kicks", "baby kicking", "feeling movement",
            "when will i feel the baby move",
        ],
        "answer": (
            "Most people first feel fetal movement between weeks 16–25. As "
            "pregnancy progresses, tracking regular kick patterns can be a "
            "helpful sign of wellbeing.\n\n🚨 A noticeable decrease or "
            "absence of movement, especially in the third trimester, should "
            "be reported to your provider right away."
        ),
    },
    {
        "id": "ultrasound",
        "category": "Baby Development",
        "keywords": ["ultrasound", "sonogram", "scan"],
        "answer": (
            "Ultrasounds help track your baby's growth, position, and "
            "development, and confirm your due date. Most pregnancies "
            "include at least one in the first trimester and one detailed "
            "anatomy scan around 18–22 weeks."
            + DISCLAIMER
        ),
    },
    {
        "id": "due_date",
        "category": "Baby Development",
        "keywords": ["due date", "when is my baby due", "estimated delivery date"],
        "answer": (
            "Your due date is usually estimated as 280 days (40 weeks) from "
            "the first day of your last menstrual period. You can calculate "
            "yours on the Pregnancy Tracker page — keep in mind it's an "
            "estimate, and only about 5% of babies arrive exactly on it."
            + DISCLAIMER
        ),
    },
    # ------------------------------------------------------------------
    # Medical / risk topics
    # ------------------------------------------------------------------
    {
        "id": "gestational_diabetes",
        "category": "Medical",
        "keywords": [
            "gestational diabetes", "high blood sugar pregnancy", "blood sugar",
        ],
        "answer": (
            "Gestational diabetes is high blood sugar that develops during "
            "pregnancy, usually diagnosed around 24–28 weeks with a glucose "
            "test. It's managed through diet, activity, monitoring, and "
            "sometimes medication.\n\n🚨 Follow your provider's monitoring "
            "plan closely, since it affects both your health and your "
            "baby's."
        ),
    },
    {
        "id": "high_blood_pressure",
        "category": "Medical",
        "keywords": [
            "high blood pressure", "hypertension", "blood pressure high",
        ],
        "answer": (
            "High blood pressure during pregnancy can increase the risk of "
            "preeclampsia and other complications. Regular monitoring, "
            "reduced salt intake, and attending all prenatal visits are "
            "important.\n\n🚨 Seek urgent care for severe headache, blurred "
            "vision, swelling of the face/hands, or chest pain."
        ),
    },
    {
        "id": "preeclampsia",
        "category": "Medical",
        "keywords": ["preeclampsia", "pre eclampsia", "toxemia"],
        "answer": (
            "Preeclampsia is a pregnancy complication marked by high blood "
            "pressure and signs of organ stress, often protein in the urine. "
            "It typically develops after 20 weeks.\n\n🚨 Warning signs — "
            "severe headache, vision changes, upper abdominal pain, or "
            "sudden swelling — need immediate medical attention."
        ),
    },
    {
        "id": "anemia",
        "category": "Medical",
        "keywords": ["anemia", "low hemoglobin"],
        "answer": (
            "Anemia (low hemoglobin) is common in pregnancy and can cause "
            "fatigue, dizziness, and shortness of breath. It's usually "
            "managed with iron-rich foods and, if needed, supplements "
            "prescribed by your provider."
            + DISCLAIMER
        ),
    },
    {
        "id": "fever",
        "category": "Medical",
        "keywords": ["fever", "high temperature", "running a temperature"],
        "answer": (
            "A fever during pregnancy should be taken seriously, since it can "
            "sometimes indicate infection.\n\n🚨 Contact your healthcare "
            "provider if your temperature is 38°C (100.4°F) or higher, or if "
            "fever is accompanied by chills, pain, or other symptoms."
        ),
    },
    {
        "id": "bleeding",
        "category": "Medical",
        "keywords": ["bleeding", "spotting", "vaginal bleeding"],
        "answer": (
            "Light spotting can sometimes be normal, especially in early "
            "pregnancy, but any bleeding should be reported to your "
            "provider.\n\n🚨 Heavy bleeding, bleeding with pain, or bleeding "
            "in the second/third trimester needs immediate medical "
            "attention — please seek emergency care."
        ),
        "urgent": True,
    },
    {
        "id": "severe_pain",
        "category": "Medical",
        "keywords": ["severe pain", "severe abdominal pain", "sharp pain"],
        "answer": (
            "🚨 Severe or persistent abdominal pain during pregnancy should "
            "be treated as an emergency. Please contact your healthcare "
            "provider or go to the nearest emergency department right away."
        ),
        "urgent": True,
    },
    {
        "id": "emergency_signs",
        "category": "Medical",
        "keywords": [
            "emergency warning signs", "when should i go to the doctor",
            "when to seek help", "warning signs",
        ],
        "answer": (
            "🚨 Seek immediate medical care if you experience:\n\n"
            "• Heavy vaginal bleeding\n"
            "• Severe abdominal pain\n"
            "• Loss of fetal movement\n"
            "• High fever\n"
            "• Severe headache with blurred vision\n\n"
            "When in doubt, it's always safer to call your provider or go to "
            "the ER."
        ),
        "urgent": True,
    },
    {
        "id": "medication_safety",
        "category": "Medical",
        "keywords": [
            "medication safety", "can i take medicine", "is this medication safe",
            "painkillers pregnancy",
        ],
        "answer": (
            "Not all medications are safe during pregnancy — this includes "
            "some common over-the-counter drugs. Always check with your "
            "doctor or pharmacist before starting, stopping, or combining any "
            "medication, including supplements."
            + DISCLAIMER
        ),
    },
    # ------------------------------------------------------------------
    # Lifestyle
    # ------------------------------------------------------------------
    {
        "id": "coffee",
        "category": "Lifestyle",
        "keywords": ["can i drink coffee", "coffee", "caffeine"],
        "answer": (
            "Yes, but caffeine intake should be limited. Most guidelines "
            "recommend keeping total caffeine (coffee, tea, soda, chocolate "
            "included) below about 200 mg per day during pregnancy."
            + DISCLAIMER
        ),
    },
    {
        "id": "tea",
        "category": "Lifestyle",
        "keywords": ["can i drink tea", "herbal tea", "tea during pregnancy"],
        "answer": (
            "Regular tea in moderation is generally fine, but be mindful of "
            "its caffeine content counting toward your daily limit. Some "
            "herbal teas aren't recommended in pregnancy, so check with your "
            "provider before trying new herbal blends."
            + DISCLAIMER
        ),
    },
    {
        "id": "traveling",
        "category": "Lifestyle",
        "keywords": ["can i travel", "traveling", "is it safe to travel"],
        "answer": (
            "Travel is generally considered safe during uncomplicated "
            "pregnancies, particularly in the second trimester. Discuss any "
            "travel plans with your provider, especially for long trips or "
            "the third trimester."
            + DISCLAIMER
        ),
    },
    {
        "id": "working",
        "category": "Lifestyle",
        "keywords": ["working during pregnancy", "can i work", "job pregnancy"],
        "answer": (
            "Most people can continue working throughout pregnancy, adjusting "
            "for comfort — regular breaks, staying hydrated, and avoiding "
            "heavy lifting or prolonged standing where possible. Physically "
            "demanding or hazardous jobs may need extra precautions — talk "
            "to your provider and employer about accommodations."
            + DISCLAIMER
        ),
    },
    {
        "id": "driving",
        "category": "Lifestyle",
        "keywords": ["can i drive", "driving pregnancy", "seatbelt pregnancy"],
        "answer": (
            "Driving is generally safe throughout pregnancy. Always wear your "
            "seatbelt with the lap belt under your bump and the shoulder belt "
            "across your chest, and take breaks on longer drives to move "
            "around."
            + DISCLAIMER
        ),
    },
    {
        "id": "air_travel",
        "category": "Lifestyle",
        "keywords": ["air travel", "flying while pregnant", "can i fly"],
        "answer": (
            "Air travel is usually fine up until around 36 weeks for "
            "uncomplicated pregnancies, though airlines vary in their "
            "policies. Walk periodically to reduce clot risk and stay "
            "hydrated.\n\n🚨 Check with your provider first if you have any "
            "pregnancy complications."
        ),
    },
    {
        "id": "vaccinations",
        "category": "Lifestyle",
        "keywords": [
            "vaccinations pregnancy", "vaccines during pregnancy", "flu shot pregnant",
        ],
        "answer": (
            "Some vaccines (like flu and whooping cough/Tdap) are commonly "
            "recommended during pregnancy, while live vaccines are generally "
            "avoided. Your provider can advise which vaccines are appropriate "
            "and when."
            + DISCLAIMER
        ),
    },
    {
        "id": "smoking",
        "category": "Lifestyle",
        "keywords": ["smoking", "smoking pregnancy", "quit smoking"],
        "answer": (
            "Smoking increases the risk of miscarriage, low birth weight, and "
            "premature birth. It's strongly recommended to stop smoking and "
            "avoid secondhand smoke — ask your provider about support "
            "resources for quitting."
            + DISCLAIMER
        ),
    },
    {
        "id": "alcohol",
        "category": "Lifestyle",
        "keywords": ["alcohol", "drinking alcohol pregnancy", "can i drink alcohol"],
        "answer": (
            "No amount of alcohol is considered safe during pregnancy, since "
            "it can affect fetal development at any stage. It's recommended "
            "to avoid alcohol entirely while pregnant."
            + DISCLAIMER
        ),
    },
    # ------------------------------------------------------------------
    # After delivery
    # ------------------------------------------------------------------
    {
        "id": "breastfeeding",
        "category": "After Delivery",
        "keywords": ["breastfeeding", "nursing", "breast milk"],
        "answer": (
            "Breastfeeding provides antibodies, nutrients, and bonding "
            "benefits for your baby, though the right feeding choice depends "
            "on your circumstances and comfort. Lactation consultants can "
            "help with latch, supply, or pain issues in the early weeks."
            + DISCLAIMER
        ),
    },
    {
        "id": "postpartum_recovery",
        "category": "After Delivery",
        "keywords": ["recovery", "postpartum recovery", "healing after birth"],
        "answer": (
            "Postpartum recovery varies — expect several weeks of physical "
            "healing (more after a C-section), vaginal bleeding that "
            "gradually tapers, and shifting hormones. Rest, gentle movement, "
            "and support from those around you all help.\n\n🚨 Heavy "
            "bleeding, fever, or severe pain after delivery need prompt "
            "medical attention."
        ),
    },
    {
        "id": "postpartum_depression",
        "category": "After Delivery",
        "keywords": [
            "postpartum depression", "baby blues", "depressed after birth",
            "sad after having a baby", "hopeless after birth",
            "crying a lot after birth", "not bonding with my baby",
            "feel sad since the baby was born", "overwhelmed after delivery",
        ],
        "answer": (
            "'Baby blues' (mild mood dips in the first two weeks) are common, "
            "but postpartum depression is more persistent — sadness, "
            "anxiety, or difficulty bonding lasting beyond two weeks.\n\n🚨 "
            "Please reach out to your healthcare provider if this sounds "
            "like what you're experiencing; effective support and treatment "
            "are available, and you don't have to go through it alone."
        ),
        "urgent": True,
    },
    {
        "id": "baby_vaccinations",
        "category": "After Delivery",
        "keywords": [
            "baby vaccinations", "newborn vaccines", "infant immunizations",
        ],
        "answer": (
            "Newborns typically follow a recommended immunization schedule "
            "starting shortly after birth, continuing through infancy. Your "
            "pediatrician will guide you through the specific schedule and "
            "timing for your baby."
            + DISCLAIMER
        ),
    },
]
