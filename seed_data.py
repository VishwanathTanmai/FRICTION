"""
seed_data.py — 120+ Real Indian Problem Statements for Fix My Itch Clone
=========================================================================

Each entry is a dict with *title*, *description*, and *category*.
Problems are written in an emotional, conversational tone and are
specific enough to suggest a startup opportunity.

Functions
---------
get_seed_problems()
    Return the full list of problem dicts.
seed_database(db_path)
    Analyse every problem with NLPEngine, insert into an SQLite DB,
    and print progress.
"""

from __future__ import annotations

import json
import os
import sqlite3
from typing import Any, Dict, List

# ======================================================================
# Seed Problems  (120+ entries, ≥10 per listed category)
# ======================================================================

SEED_PROBLEMS: List[Dict[str, str]] = [
    # ── Health (12) ──────────────────────────────────────────────────
    {
        "title": "Why can't anxious people find trustworthy non-prescription sleep solutions easily?",
        "description": (
            "Millions of Indians struggle with insomnia and anxiety but have no reliable, "
            "affordable way to access evidence-based sleep aids without visiting a doctor. "
            "OTC options are confusing and often adulterated."
        ),
        "category": "Health",
    },
    {
        "title": "Public hospitals are a nightmare — why do patients wait 6 hours just to see a doctor?",
        "description": (
            "Government hospitals are overcrowded and understaffed. Patients from rural areas "
            "travel hundreds of kilometres only to sit in terrible queues all day. Many give up "
            "and go home untreated."
        ),
        "category": "Health",
    },
    {
        "title": "My elderly parents can't track their medicines properly and nobody helps!",
        "description": (
            "Senior citizens in India take multiple medications daily but have no simple tool "
            "to manage dosages, refills, and drug interactions. Missed doses lead to hospital "
            "readmissions that are expensive and stressful."
        ),
        "category": "Health",
    },
    {
        "title": "Why is mental health support still a taboo? I can't find an affordable therapist anywhere!",
        "description": (
            "India has fewer than 1 psychiatrist per 100,000 people. The stigma around mental "
            "health means most people suffer silently. Online therapy is either unreliable or "
            "too expensive for the average Indian."
        ),
        "category": "Health",
    },
    {
        "title": "Fake medicines are killing people and nobody seems to care!",
        "description": (
            "Counterfeit drugs account for up to 25%% of the Indian pharma market. Patients "
            "have no easy way to verify whether a medicine is genuine before consuming it. "
            "The consequences can be fatal."
        ),
        "category": "Health",
    },
    {
        "title": "Why is it so hard to find a blood donor in an emergency at 2 AM?",
        "description": (
            "Blood banks are fragmented and most don't have real-time inventory data. During "
            "emergencies, families desperately call dozens of people. A digital matching platform "
            "could save thousands of lives every year."
        ),
        "category": "Health",
    },
    {
        "title": "Pregnant women in villages have zero access to prenatal care — how is that acceptable?",
        "description": (
            "Rural India's maternal mortality rate is shockingly high because women can't access "
            "regular check-ups, ultrasounds, or trained midwives. Telemedicine could bridge this "
            "gap but adoption is almost zero."
        ),
        "category": "Health",
    },
    {
        "title": "Diabetes is an epidemic but nobody teaches Indians how to actually manage it daily!",
        "description": (
            "India has 100+ million diabetics but most rely on occasional doctor visits instead "
            "of daily monitoring. There's no affordable, culturally relevant platform that helps "
            "track sugar levels, diet, and exercise."
        ),
        "category": "Health",
    },
    {
        "title": "Ambulances take forever to arrive — people die waiting in traffic!",
        "description": (
            "Emergency response times in Indian cities average 20–45 minutes due to traffic "
            "congestion and poor dispatch systems. An Uber-like ambulance network with GPS "
            "routing could dramatically reduce response time."
        ),
        "category": "Health",
    },
    {
        "title": "Why do diagnostic labs charge wildly different prices for the same blood test?",
        "description": (
            "A CBC test can cost ₹150 at one lab and ₹800 at another just 2 km away. There's "
            "no transparency in diagnostic pricing and patients have no way to compare quality "
            "and cost before booking."
        ),
        "category": "Health",
    },
    {
        "title": "My grandmother needs physiotherapy but the nearest physio is 50 km away!",
        "description": (
            "Physiotherapy is essential for post-surgery recovery and chronic pain but "
            "physiotherapists are concentrated in cities. Rural and semi-urban patients "
            "simply go without, leading to permanent disability."
        ),
        "category": "Health",
    },
    {
        "title": "Why can't I get a simple online second opinion without paying a fortune?",
        "description": (
            "After a serious diagnosis, patients want to verify it with another doctor but "
            "booking a second consultation is expensive and time-consuming. A streamlined "
            "telemedicine second-opinion service is desperately needed."
        ),
        "category": "Health",
    },

    # ── Finance (12) ─────────────────────────────────────────────────
    {
        "title": "Small shopkeepers can't get a ₹50,000 loan without begging the bank for months!",
        "description": (
            "Micro-entrepreneurs in India face impossible documentation requirements for small "
            "loans. Banks don't consider cash-flow data from UPI or daily sales. Millions remain "
            "stuck with predatory moneylenders."
        ),
        "category": "Finance",
    },
    {
        "title": "I have no idea where my salary disappears every month — budgeting apps don't work for Indians!",
        "description": (
            "Most budgeting apps are designed for Western lifestyles. They don't handle cash "
            "spending, split family expenses, or festival-season surges. Indians need a "
            "culturally aware personal finance tool."
        ),
        "category": "Finance",
    },
    {
        "title": "Insurance claims are a scam — they reject everything and nobody can fight back!",
        "description": (
            "Health and motor insurance companies in India routinely reject or delay legitimate "
            "claims using fine-print exclusions. Policyholders have no affordable legal recourse "
            "and feel completely helpless."
        ),
        "category": "Finance",
    },
    {
        "title": "Why do farmers still depend on loan sharks when banks literally exist?",
        "description": (
            "Formal credit for farmers involves endless paperwork, land title disputes, and "
            "months of waiting. Informal lenders charge 36–60%% interest. A digital "
            "credit-scoring system using crop and weather data could fix this."
        ),
        "category": "Finance",
    },
    {
        "title": "Tax filing in India is so confusing that even CAs make mistakes!",
        "description": (
            "The Indian tax system has dozens of exemptions, deductions, and forms. Salaried "
            "people overpay because they don't understand Section 80C, HRA, or new-vs-old "
            "regime choices. Automated advisory is desperately needed."
        ),
        "category": "Finance",
    },
    {
        "title": "UPI frauds are exploding and there's no real way for common people to get their money back!",
        "description": (
            "Thousands of Indians lose money daily to UPI phishing and fraud. The complaint "
            "process is broken — police don't register FIRs, banks pass the buck, and victims "
            "give up. Real-time fraud detection is critical."
        ),
        "category": "Finance",
    },
    {
        "title": "Why is mutual fund investing still so intimidating for first-time Indian investors?",
        "description": (
            "Despite 'Mutual Funds Sahi Hai' campaigns, most Indians are scared of investing "
            "because jargon is overwhelming and past scams eroded trust. A truly simple, "
            "vernacular-first investment platform could unlock a massive market."
        ),
        "category": "Finance",
    },
    {
        "title": "Retired government employees wait months for their pension — that's their survival money!",
        "description": (
            "Pension disbursement in India is plagued by delays, paperwork errors, and "
            "corruption. Senior citizens who depend entirely on pensions face months without "
            "income. Digitising the pipeline end-to-end is overdue."
        ),
        "category": "Finance",
    },
    {
        "title": "Micro-savings for daily-wage workers don't exist — where do they put ₹20 a day?",
        "description": (
            "Daily-wage earners want to save but no bank product accepts ₹10–50 deposits "
            "conveniently. Digital wallets don't offer savings features. A micro-savings "
            "platform linked to UPI could serve 300 million workers."
        ),
        "category": "Finance",
    },
    {
        "title": "Gold loan interest rates are a rip-off and borrowers have no transparency!",
        "description": (
            "Indians pledge gold worth ₹5 lakh crore annually but interest rates vary from "
            "7%% to 36%% with hidden charges. A comparison and monitoring platform would "
            "empower millions of borrowers."
        ),
        "category": "Finance",
    },
    {
        "title": "Women in rural India have zero financial literacy — they don't even know about Jan Dhan accounts!",
        "description": (
            "Despite government schemes, rural women remain financially excluded because "
            "nobody explains banking in their language. A voice-based, vernacular financial "
            "literacy app could transform their lives."
        ),
        "category": "Finance",
    },
    {
        "title": "Chit fund scams keep happening because there's no digital oversight!",
        "description": (
            "Informal chit funds manage crores in India but operate with zero digital records. "
            "Organisers vanish with money regularly. A regulated, transparent digital chit "
            "platform could protect millions of investors."
        ),
        "category": "Finance",
    },

    # ── Education (12) ───────────────────────────────────────────────
    {
        "title": "Government school teachers don't teach — students learn nothing for 10 years!",
        "description": (
            "Millions of children in government schools can't read basic sentences even in "
            "Class 5 because teachers are absent or untrained. No accountability exists. "
            "Technology-assisted learning could supplement classroom gaps."
        ),
        "category": "Education",
    },
    {
        "title": "Why do Indian students spend ₹2 lakh on coaching that doesn't even guarantee results?",
        "description": (
            "The coaching industry exploits parental anxiety around JEE/NEET. Students "
            "are packed into mega-batches with no personalisation. An AI-powered adaptive "
            "learning platform could deliver better outcomes at a fraction of the cost."
        ),
        "category": "Education",
    },
    {
        "title": "Rural children have smartphones but no quality educational content in their language!",
        "description": (
            "While internet penetration has reached villages, educational content is "
            "predominantly in English or Hindi. Children speaking Odia, Telugu, or Marathi "
            "are left behind. Vernacular ed-tech is a massive opportunity."
        ),
        "category": "Education",
    },
    {
        "title": "College placement cells are useless — students graduate with zero job-ready skills!",
        "description": (
            "Most Indian colleges focus on rote learning and outdated curricula. Placement "
            "cells operate on personal connections rather than skill matching. A platform "
            "bridging skill gaps with employer needs is desperately needed."
        ),
        "category": "Education",
    },
    {
        "title": "Special-needs children have almost no access to trained educators in India!",
        "description": (
            "Children with learning disabilities, autism, or ADHD are routinely ignored by "
            "mainstream schools. Trained special educators are extremely rare outside metros. "
            "Digital therapy and training tools could fill this gap."
        ),
        "category": "Education",
    },
    {
        "title": "Why is vocational training looked down upon when India desperately needs skilled workers?",
        "description": (
            "ITI and polytechnic graduates face social stigma despite massive demand for "
            "plumbers, electricians, and welders. A platform that connects skilled workers "
            "with dignified employment could change perceptions."
        ),
        "category": "Education",
    },
    {
        "title": "Exam cheating mafias operate openly — how can honest students compete?",
        "description": (
            "Paper leaks and impersonation scandals plague exams from SSC to NEET. Honest "
            "students lose seats they deserve. AI-proctored, blockchain-verified examination "
            "systems could restore integrity."
        ),
        "category": "Education",
    },
    {
        "title": "Parents have no idea what career options exist beyond doctor, engineer, or MBA!",
        "description": (
            "Career counselling is non-existent in most Indian schools. Parents push children "
            "into a handful of streams out of ignorance. An AI career advisor using aptitude "
            "data could open up hundreds of pathways."
        ),
        "category": "Education",
    },
    {
        "title": "Digital divide: kids in tribal areas can't attend online classes even with free data!",
        "description": (
            "Low-cost smartphones have tiny screens, poor speakers, and limited storage. Online "
            "classes designed for 4G broadband simply don't work for tribal and rural students. "
            "Offline-first, low-bandwidth solutions are essential."
        ),
        "category": "Education",
    },
    {
        "title": "Scholarship money gets stuck in bureaucracy — deserving students drop out while waiting!",
        "description": (
            "Government scholarships for SC/ST/OBC students involve complex applications and "
            "delayed disbursements. Students give up on higher education because they can't "
            "afford even one semester while waiting."
        ),
        "category": "Education",
    },
    {
        "title": "Why don't our schools teach financial literacy, coding, or critical thinking?",
        "description": (
            "Indian curricula remain stuck in the 20th century while the world demands "
            "computational thinking, financial literacy, and creativity. An after-school "
            "platform for 21st-century skills has a huge addressable market."
        ),
        "category": "Education",
    },
    {
        "title": "College hostel conditions are horrific — nobody inspects or rates them!",
        "description": (
            "Students live in overcrowded, unhygienic hostels with no complaint mechanism. "
            "A transparent rating and review platform for hostels would empower students "
            "and force colleges to improve."
        ),
        "category": "Education",
    },

    # ── Logistics (10) ───────────────────────────────────────────────
    {
        "title": "Last-mile delivery in tier-3 towns is unreliable — parcels arrive damaged or never!",
        "description": (
            "E-commerce returns in small towns are 3x higher than metros because of poor "
            "last-mile logistics. Delivery partners don't have proper addresses and packages "
            "get lost. A hyperlocal delivery network is needed."
        ),
        "category": "Logistics",
    },
    {
        "title": "Cold chain breaks kill tonnes of fresh produce every year — farmers lose everything!",
        "description": (
            "India wastes 30%% of fruits and vegetables due to broken cold chains between "
            "farms and markets. IoT-based temperature monitoring and shared cold storage "
            "could save ₹90,000 crore annually."
        ),
        "category": "Logistics",
    },
    {
        "title": "Truck drivers waste 60%% of their time waiting for return loads — that's insane!",
        "description": (
            "India's trucking industry is fragmented with millions of small operators. Trucks "
            "often return empty because there's no real-time load-matching platform. An Uber-for-"
            "freight app could save billions in fuel."
        ),
        "category": "Logistics",
    },
    {
        "title": "Inter-city courier takes 7 days when it should take 2 — where do packages disappear?",
        "description": (
            "Domestic courier in India passes through too many hubs with manual sorting. "
            "Tracking is unreliable and customer support is non-existent. Automated sorting "
            "and direct routing could halve delivery times."
        ),
        "category": "Logistics",
    },
    {
        "title": "Moving houses in India is a nightmare — packers and movers cheat openly!",
        "description": (
            "The relocation industry is unregulated. Movers quote low, hold goods hostage, "
            "and demand extra payment. There's no standardised pricing, insurance, or review "
            "system. A trusted platform is urgently needed."
        ),
        "category": "Logistics",
    },
    {
        "title": "Warehousing for small e-commerce sellers is impossibly expensive!",
        "description": (
            "Small online sellers can't afford dedicated warehouse space but need proper "
            "storage for inventory. Shared, pay-per-use micro-warehousing with fulfilment "
            "services could democratise e-commerce logistics."
        ),
        "category": "Logistics",
    },
    {
        "title": "Why do I have to track my own shipment across 5 different courier apps?",
        "description": (
            "Indians shop from multiple e-commerce platforms, each using different couriers. "
            "A universal shipment tracker that aggregates all deliveries in one dashboard "
            "would save millions of hours of frustration."
        ),
        "category": "Logistics",
    },
    {
        "title": "Medical supply chains to PHCs are broken — rural clinics run out of basic drugs!",
        "description": (
            "Primary Health Centres in rural India frequently run out of essential medicines "
            "because supply chain data is paper-based and nobody monitors stock in real time. "
            "Digital inventory tracking is a life-saving need."
        ),
        "category": "Logistics",
    },
    {
        "title": "Local kirana shops can't compete with quick-commerce because their supply chain is chaotic!",
        "description": (
            "Small grocery stores order from multiple wholesalers with inconsistent pricing "
            "and delivery. A B2B ordering platform with next-day delivery and credit could "
            "empower 12 million kiranas to survive."
        ),
        "category": "Logistics",
    },
    {
        "title": "Reverse logistics for returns is a mess — e-commerce companies eat the cost!",
        "description": (
            "Product returns in India are expensive because reverse logistics infrastructure "
            "barely exists. Returned goods pile up in warehouses without grading or resale "
            "channels. A returns-management platform is needed."
        ),
        "category": "Logistics",
    },

    # ── Food (10) ────────────────────────────────────────────────────
    {
        "title": "Street food is delicious but terrifyingly unhygienic — who monitors it?",
        "description": (
            "Millions eat street food daily but hygiene standards are non-existent. Food "
            "poisoning cases go unreported. A crowd-sourced hygiene rating and vendor "
            "certification platform could protect consumers."
        ),
        "category": "Food",
    },
    {
        "title": "Why is organic food 3x more expensive when farmers barely earn anything extra?",
        "description": (
            "Middlemen and certification costs inflate organic food prices. Farmers get ₹2 "
            "more per kg while consumers pay ₹100 more. A direct farm-to-consumer marketplace "
            "could make organic food affordable."
        ),
        "category": "Food",
    },
    {
        "title": "Food delivery apps charge 30%% commission — small restaurants are dying!",
        "description": (
            "Zomato and Swiggy's commissions make small restaurant businesses unviable. "
            "Restaurant owners can't negotiate and have no alternative. A cooperative delivery "
            "platform with fair pricing could save them."
        ),
        "category": "Food",
    },
    {
        "title": "School mid-day meals are often inedible — children eat because they're starving, not because it's food!",
        "description": (
            "Mid-day meal quality varies wildly across states. Dead insects, stones, and "
            "spoiled ingredients are regularly found. Digital monitoring with photo verification "
            "and feedback loops could improve quality."
        ),
        "category": "Food",
    },
    {
        "title": "I'm diabetic and there's no easy way to order truly sugar-free Indian food!",
        "description": (
            "Diabetic-friendly food options on delivery apps are misleading. 'Sugar-free' "
            "labels hide refined carbs. A specialised platform for medically verified "
            "diabetic meals could serve 100 million Indians."
        ),
        "category": "Food",
    },
    {
        "title": "Food waste from weddings could feed thousands — why isn't there a redistribution network?",
        "description": (
            "Indian weddings waste tonnes of food while millions go hungry. NGOs exist but "
            "lack real-time coordination to collect and distribute excess food before it "
            "spoils. A tech-enabled redistribution platform is essential."
        ),
        "category": "Food",
    },
    {
        "title": "Milk adulteration is rampant — how do I know if my children's milk is safe?",
        "description": (
            "Synthetic milk and water-diluted milk are widespread in India. FSSAI testing "
            "is infrequent and consumers have no portable testing tools. A simple at-home "
            "testing kit or verified supply chain could help."
        ),
        "category": "Food",
    },
    {
        "title": "Why can't working professionals in tier-2 cities find healthy tiffin services?",
        "description": (
            "Home-cooked tiffin services exist but are informal, unreliable, and have no "
            "quality standards. A platform connecting verified home cooks with health-"
            "conscious professionals could create a huge market."
        ),
        "category": "Food",
    },
    {
        "title": "Grocery prices vary 40%% between shops in the same locality — there's zero price transparency!",
        "description": (
            "Consumers overpay for groceries because there's no easy price comparison tool "
            "for local shops. A hyperlocal price transparency app could save families "
            "thousands of rupees monthly."
        ),
        "category": "Food",
    },
    {
        "title": "Restaurant kitchen hygiene is a black box — FSSAI licenses mean nothing!",
        "description": (
            "An FSSAI licence is easy to obtain but impossible to enforce. Restaurant "
            "kitchens can be filthy behind closed doors. IoT-based kitchen monitoring "
            "and real-time hygiene scores could protect consumers."
        ),
        "category": "Food",
    },

    # ── Legal (10) ───────────────────────────────────────────────────
    {
        "title": "Cases take 30 years in Indian courts — justice delayed is justice denied!",
        "description": (
            "India has 5 crore+ pending cases. Common people can't afford decades of "
            "litigation. AI-assisted case prioritisation and online dispute resolution "
            "could dramatically reduce the backlog."
        ),
        "category": "Legal",
    },
    {
        "title": "Tenants have zero legal protection — landlords throw people out overnight!",
        "description": (
            "Rental agreements are one-sided and enforcement is weak. Tenants face illegal "
            "evictions, deposit theft, and harassment with no affordable legal recourse. "
            "A tenant rights platform with legal aid could help millions."
        ),
        "category": "Legal",
    },
    {
        "title": "Women can't file domestic violence complaints safely — the system re-traumatises them!",
        "description": (
            "Filing a domestic violence case requires visiting a police station, which is "
            "intimidating and often unsafe. An anonymous digital reporting tool with legal "
            "guidance could encourage more women to seek help."
        ),
        "category": "Legal",
    },
    {
        "title": "Property registration is a corruption hotspot — bribes are expected at every step!",
        "description": (
            "Registering property in India involves sub-registrar offices where officials "
            "openly demand bribes. The process is opaque, slow, and paper-based. Digital "
            "registration with transparent pricing could end this."
        ),
        "category": "Legal",
    },
    {
        "title": "Nobody reads the fine print in loan agreements — and banks exploit that!",
        "description": (
            "Loan documents are deliberately complex with hidden clauses about variable rates, "
            "foreclosure charges, and penalties. An AI tool that summarises and flags risky "
            "clauses in plain Hindi/English is badly needed."
        ),
        "category": "Legal",
    },
    {
        "title": "Consumer complaints go nowhere — companies ignore them because there's no consequence!",
        "description": (
            "Consumer forums are slow and underfunded. Companies know that most consumers will "
            "give up before getting resolution. A platform that aggregates complaints and "
            "applies social pressure could change the game."
        ),
        "category": "Legal",
    },
    {
        "title": "Getting a police FIR registered is itself a fight — victims become suspects!",
        "description": (
            "Police stations routinely refuse to register FIRs for theft, fraud, and assault. "
            "Victims are harassed, questioned, and turned away. An e-FIR system with "
            "automatic acknowledgement could fix this."
        ),
        "category": "Legal",
    },
    {
        "title": "Labour contract workers have no idea about their legal rights!",
        "description": (
            "Contract labourers in factories, construction, and services are routinely denied "
            "minimum wage, PF, and insurance. They don't know the law protects them. A "
            "multilingual rights awareness chatbot could empower millions."
        ),
        "category": "Legal",
    },
    {
        "title": "Divorce proceedings in India are emotionally and financially devastating!",
        "description": (
            "Contested divorces take 5-15 years and cost lakhs. Mediation services are rare "
            "and expensive. A low-cost digital mediation and legal advisory platform could "
            "make separation less traumatic."
        ),
        "category": "Legal",
    },
    {
        "title": "RTI applications get delayed or ignored — citizens can't hold government accountable!",
        "description": (
            "Filing RTI requests is cumbersome, responses are delayed, and appeals are "
            "complicated. A platform that simplifies RTI filing, tracks responses, and "
            "escalates automatically could strengthen democracy."
        ),
        "category": "Legal",
    },

    # ── Transport (10) ───────────────────────────────────────────────
    {
        "title": "Auto-rickshaw drivers refuse meters and overcharge — commuters have no power!",
        "description": (
            "In most Indian cities, auto-rickshaws operate without meters and charge arbitrary "
            "fares. Commuters, especially women, are left haggling or paying 2-3x the legal "
            "fare. App-based fair pricing could solve this."
        ),
        "category": "Transport",
    },
    {
        "title": "Public buses are so unreliable that people arrive late to work every single day!",
        "description": (
            "Bus schedules exist on paper but buses run erratically. Workers spend 3-4 hours "
            "daily commuting because they can't predict when the bus will arrive. Real-time "
            "GPS tracking and arrival predictions are missing."
        ),
        "category": "Transport",
    },
    {
        "title": "Getting a driving licence without paying a bribe feels almost impossible!",
        "description": (
            "RTO offices are notorious corruption centres. Even qualified candidates are "
            "failed deliberately so they pay agents. Automated, AI-proctored driving tests "
            "could eliminate human discretion and corruption."
        ),
        "category": "Transport",
    },
    {
        "title": "Women feel unsafe in shared cabs and autos at night — why is safety an afterthought?",
        "description": (
            "Late-night commuting is dangerous for women. Existing ride-hailing apps don't "
            "do enough for safety — SOS buttons don't work, drivers aren't verified properly. "
            "A women-first safety-focused transport service is needed."
        ),
        "category": "Transport",
    },
    {
        "title": "Parking in any Indian city is pure chaos — you circle for 30 minutes daily!",
        "description": (
            "Indian cities lose millions of productive hours to parking hunts. There's no "
            "real-time information about parking availability. A smart parking platform with "
            "sensor data and pre-booking could transform urban mobility."
        ),
        "category": "Transport",
    },
    {
        "title": "Electric vehicle charging stations are almost non-existent outside metros!",
        "description": (
            "India is pushing EVs but charging infrastructure is abysmal in tier-2 and tier-3 "
            "cities. Buyers suffer range anxiety and avoid EVs. A crowd-funded community "
            "charging network could accelerate adoption."
        ),
        "category": "Transport",
    },
    {
        "title": "Potholes damage my car every monsoon and nobody compensates for the repairs!",
        "description": (
            "Indian roads develop dangerous potholes every rainy season. Citizens report them "
            "but repair takes months. A crowd-sourced pothole mapping and accountability "
            "platform could force faster repairs."
        ),
        "category": "Transport",
    },
    {
        "title": "Train ticket waitlists are a gamble — I never know if I'll actually get to travel!",
        "description": (
            "Millions book waitlisted Indian Railway tickets hoping for confirmation. Most "
            "don't get confirmed and scramble for alternatives at the last minute. A "
            "probability predictor with alternative suggestions could help."
        ),
        "category": "Transport",
    },
    {
        "title": "Intercity bus booking is a mess — agents give you the worst seats and pocket commissions!",
        "description": (
            "Bus booking through agents involves hidden commissions and poor seat selection. "
            "Online platforms exist but coverage of private operators in smaller towns is "
            "incomplete. A universal bus aggregator is needed."
        ),
        "category": "Transport",
    },
    {
        "title": "School vans are unsafe and overcrowded — parents worry every single day!",
        "description": (
            "School transport in India is largely unregulated. Vans carry double capacity "
            "with untrained drivers. GPS tracking is rare. A safe school transport platform "
            "with real-time tracking could ease parental anxiety."
        ),
        "category": "Transport",
    },

    # ── Housing (10) ─────────────────────────────────────────────────
    {
        "title": "Buying a flat in India is a trust exercise — builders delay possession by years!",
        "description": (
            "Homebuyers pay EMIs for years on undelivered flats. RERA exists but enforcement "
            "is weak. A real-time project tracking and builder accountability platform could "
            "protect crores of buyers."
        ),
        "category": "Housing",
    },
    {
        "title": "Rental brokers charge one month's rent as commission for showing 3 flats — it's extortion!",
        "description": (
            "Real estate brokers in Indian cities charge 1-2 months' rent as brokerage. "
            "They add no real value and often show misleading listings. Zero-brokerage "
            "platforms exist but need better trust mechanisms."
        ),
        "category": "Housing",
    },
    {
        "title": "Society maintenance is mismanaged — nobody knows where the money goes!",
        "description": (
            "Housing society committees collect lakhs in maintenance but accounting is opaque. "
            "Residents suspect corruption but can't audit easily. A digital society management "
            "platform with transparent accounting could fix this."
        ),
        "category": "Housing",
    },
    {
        "title": "Finding PG accommodation as a single woman in a new city is terrifying!",
        "description": (
            "Women moving to new cities for work face unsafe PG accommodations, discriminatory "
            "landlords, and no verified listings. A women-focused, safety-verified "
            "accommodation platform is badly needed."
        ),
        "category": "Housing",
    },
    {
        "title": "Why do landlords discriminate based on religion and food habits? It's 2025!",
        "description": (
            "Muslim and non-vegetarian tenants face systematic discrimination in Indian "
            "rental markets. Landlords openly reject tenants based on religion. A bias-free "
            "rental matching platform could challenge this."
        ),
        "category": "Housing",
    },
    {
        "title": "Home loan processing takes 3 months and involves 50 documents — why so complicated?",
        "description": (
            "Getting a home loan in India requires mountains of paperwork, multiple office "
            "visits, and opaque eligibility criteria. A fully digital, instant pre-approval "
            "platform could save millions of hours."
        ),
        "category": "Housing",
    },
    {
        "title": "Affordable housing doesn't mean liveable housing — PMAY flats are falling apart!",
        "description": (
            "Government affordable housing schemes deliver poor-quality construction. Walls "
            "crack within months, plumbing fails, and there's no grievance mechanism. "
            "Quality monitoring with IoT sensors could ensure standards."
        ),
        "category": "Housing",
    },
    {
        "title": "Nobody can verify property ownership properly — duplicate titles are everywhere!",
        "description": (
            "India's land records system is archaic and fraud-ridden. Buyers get cheated with "
            "duplicate or forged title deeds. Blockchain-based land registries could eliminate "
            "ownership disputes permanently."
        ),
        "category": "Housing",
    },
    {
        "title": "Renting furniture for a temporary stay is either expensive or the quality is garbage!",
        "description": (
            "Young professionals who relocate frequently need furniture rental but existing "
            "services are overpriced with hidden charges and damaged products. A quality-first "
            "rental marketplace could capture this growing segment."
        ),
        "category": "Housing",
    },
    {
        "title": "Water supply in new apartments is unreliable — tanker mafia controls everything!",
        "description": (
            "Builders promise 24/7 water but deliver nothing. Residents depend on expensive "
            "water tankers controlled by local mafias. A community water management platform "
            "with rainwater harvesting solutions is needed."
        ),
        "category": "Housing",
    },

    # ── Agriculture (10) ─────────────────────────────────────────────
    {
        "title": "Farmers sell tomatoes at ₹2/kg while consumers buy at ₹60/kg — where does the money go?",
        "description": (
            "India's agricultural supply chain has 5-6 middlemen between farmer and consumer. "
            "Farmers get a fraction of the retail price. A direct farm-to-consumer platform "
            "could double farmer income and cut consumer costs."
        ),
        "category": "Agriculture",
    },
    {
        "title": "Weather forecasts for Indian farmers are useless — they need field-level predictions!",
        "description": (
            "IMD forecasts cover districts, not individual farms. Farmers make planting and "
            "harvesting decisions based on outdated information. Hyper-local weather alerts "
            "using AI and IoT sensors could prevent massive crop losses."
        ),
        "category": "Agriculture",
    },
    {
        "title": "Crop insurance claims take so long that farmers commit suicide waiting!",
        "description": (
            "PMFBY crop insurance is supposed to protect farmers but claims assessment is "
            "slow, corrupt, and opaque. Satellite-based automatic crop damage assessment "
            "could process claims in days instead of months."
        ),
        "category": "Agriculture",
    },
    {
        "title": "Pesticide overuse is poisoning our food and soil — farmers don't know the right dosage!",
        "description": (
            "Indian farmers overuse pesticides because they can't diagnose crop diseases "
            "properly. An AI-powered crop disease identification app using phone cameras "
            "could recommend precise treatments and save lives."
        ),
        "category": "Agriculture",
    },
    {
        "title": "Mandi prices fluctuate wildly — farmers have no bargaining power!",
        "description": (
            "APMC mandi rates change daily and farmers who arrive with perishable goods have "
            "no choice but to accept whatever middlemen offer. Real-time price transparency "
            "and digital auction platforms could empower farmers."
        ),
        "category": "Agriculture",
    },
    {
        "title": "Soil testing is almost impossible to access for small farmers!",
        "description": (
            "Soil health cards exist on paper but actual testing facilities are rare and "
            "samples take months to process. A portable, affordable soil testing kit with "
            "instant digital results could revolutionise farming."
        ),
        "category": "Agriculture",
    },
    {
        "title": "Farm equipment is too expensive to own — why can't farmers share tractors?",
        "description": (
            "Small farmers can't afford tractors, harvesters, or drones individually. An "
            "Uber-for-farm-equipment platform where farmers rent by the hour could make "
            "modern farming accessible and affordable."
        ),
        "category": "Agriculture",
    },
    {
        "title": "Post-harvest storage doesn't exist for small farmers — they're forced to sell immediately!",
        "description": (
            "Without cold storage, farmers must sell perishables within days of harvest, "
            "depressing prices. Community-owned, solar-powered cold storage units managed "
            "through an app could give farmers market timing power."
        ),
        "category": "Agriculture",
    },
    {
        "title": "Organic certification is too expensive and complicated for small-scale farmers!",
        "description": (
            "Getting organic certification costs ₹30,000-50,000 and takes years of paperwork. "
            "Small farmers who already practice organic methods can't afford it. A group "
            "certification and blockchain traceability model could help."
        ),
        "category": "Agriculture",
    },
    {
        "title": "Water irrigation wastes 60%% because farmers flood fields instead of drip-irrigating!",
        "description": (
            "Flood irrigation wastes massive amounts of water because drip systems are "
            "expensive and farmers lack technical knowledge. Subsidised smart irrigation "
            "kits with mobile monitoring could save India's groundwater."
        ),
        "category": "Agriculture",
    },

    # ── Environment (10) ─────────────────────────────────────────────
    {
        "title": "Delhi's air is literally killing people — why can't we even measure pollution accurately?",
        "description": (
            "Air quality monitoring stations are sparse and data is unreliable. Citizens "
            "have no hyperlocal pollution data to make informed decisions. Low-cost IoT air "
            "quality sensors in every neighbourhood could save lives."
        ),
        "category": "Environment",
    },
    {
        "title": "Plastic waste segregation at home is pointless when it all gets mixed up by the collector!",
        "description": (
            "Even when citizens segregate waste, collection systems dump everything together. "
            "A tech-enabled waste collection network with verified segregation and recycler "
            "connections could make segregation meaningful."
        ),
        "category": "Environment",
    },
    {
        "title": "Rivers are dying because sewage treatment plants don't actually work!",
        "description": (
            "Most STPs in India operate at a fraction of capacity or not at all. Untreated "
            "sewage flows directly into rivers. Real-time IoT monitoring of STP performance "
            "with public dashboards could force accountability."
        ),
        "category": "Environment",
    },
    {
        "title": "E-waste from old phones and laptops is handled by dangerous informal recyclers!",
        "description": (
            "Indians discard millions of electronics annually but formal e-waste recycling "
            "infrastructure barely exists. Informal recyclers extract metals using acid baths "
            "without safety gear. A safe, convenient e-waste collection service is urgent."
        ),
        "category": "Environment",
    },
    {
        "title": "Tree cutting for construction goes unreported — cities are losing their green cover!",
        "description": (
            "Urban trees are cut illegally for construction projects. Citizens can report "
            "but the process is slow and consequences are minimal. Satellite-based tree "
            "cover monitoring with automatic alerts could deter illegal felling."
        ),
        "category": "Environment",
    },
    {
        "title": "Groundwater levels are dropping alarmingly but nobody tracks individual borewell usage!",
        "description": (
            "India is the world's largest groundwater user but there's zero regulation at "
            "the individual borewell level. IoT-based water metering with community dashboards "
            "could encourage conservation before aquifers run dry."
        ),
        "category": "Environment",
    },
    {
        "title": "Construction dust is a silent killer — builders face zero penalties!",
        "description": (
            "Construction sites in Indian cities generate massive dust pollution but compliance "
            "with anti-pollution norms is negligible. Automated dust monitoring with real-time "
            "regulatory reporting could force compliance."
        ),
        "category": "Environment",
    },
    {
        "title": "Why can't Indian cities compost their organic waste instead of dumping it in landfills?",
        "description": (
            "60%% of Indian municipal waste is organic and compostable but it ends up in "
            "overflowing landfills. Decentralised composting with community participation "
            "and compost marketplace could turn waste into wealth."
        ),
        "category": "Environment",
    },
    {
        "title": "Solar panel adoption is slow because financing and installation are both painful!",
        "description": (
            "Rooftop solar makes economic sense for millions of Indian homes but upfront "
            "cost, confusing subsidies, and unreliable installers hold people back. A one-stop "
            "solar platform with financing could accelerate adoption."
        ),
        "category": "Environment",
    },
    {
        "title": "Lakes are encroached and polluted — Bengaluru's lakes literally catch fire!",
        "description": (
            "Urban lakes in India are treated as dumping grounds. Industrial effluents and "
            "sewage turn them toxic. A citizen-powered lake monitoring and restoration "
            "platform with government integration could revive water bodies."
        ),
        "category": "Environment",
    },

    # ── Technology (10) ──────────────────────────────────────────────
    {
        "title": "Internet speeds in rural India are terrible — 4G is just a label, not reality!",
        "description": (
            "Telecom companies advertise 4G coverage but actual speeds in rural areas are "
            "often below 1 Mbps. Students can't attend online classes, farmers can't access "
            "market prices. Last-mile connectivity solutions are critical."
        ),
        "category": "Technology",
    },
    {
        "title": "Government websites are so bad that citizens give up and pay touts instead!",
        "description": (
            "E-governance portals crash during peak hours, have terrible UX, and are "
            "mobile-unfriendly. Citizens pay middlemen to navigate the system. Modern, "
            "reliable, mobile-first redesigns could save millions in corruption."
        ),
        "category": "Technology",
    },
    {
        "title": "Cyberbullying is destroying Indian teenagers and platforms do nothing!",
        "description": (
            "Online harassment on social media is rampant among Indian teens. Platforms are "
            "slow to respond and parents are clueless. AI-powered monitoring tools that "
            "alert parents and schools could prevent tragedies."
        ),
        "category": "Technology",
    },
    {
        "title": "Elderly parents can't use smartphones properly — apps are designed for young people!",
        "description": (
            "India's 130+ million senior citizens are digitally excluded because apps have "
            "tiny text, complex navigation, and English-only interfaces. An elder-friendly "
            "app launcher with voice control could bridge the digital divide."
        ),
        "category": "Technology",
    },
    {
        "title": "Data privacy is a joke in India — apps collect everything without real consent!",
        "description": (
            "Indian apps harvest personal data aggressively with dark-pattern consent flows. "
            "Users don't understand what they're agreeing to. A privacy audit tool that "
            "scans app permissions and explains risks could empower users."
        ),
        "category": "Technology",
    },
    {
        "title": "Vernacular internet content is sparse — 90%% of useful content is in English!",
        "description": (
            "India has 500+ million internet users who prefer non-English languages but most "
            "quality content is English-only. AI-powered content translation and creation "
            "in vernacular languages is a massive untapped opportunity."
        ),
        "category": "Technology",
    },
    {
        "title": "Small businesses can't afford custom software — they run on WhatsApp and notebooks!",
        "description": (
            "MSMEs manage inventory, billing, and customers manually because enterprise "
            "software is expensive and complex. A simple, affordable, mobile-first business "
            "management suite in vernacular languages could serve millions."
        ),
        "category": "Technology",
    },
    {
        "title": "Online exam proctoring is invasive and doesn't even catch real cheaters!",
        "description": (
            "Current proctoring tools require constant webcam access, flag innocent movements, "
            "and still miss organised cheating syndicates. AI-based behavioural analysis "
            "rather than surveillance could be more effective and humane."
        ),
        "category": "Technology",
    },
    {
        "title": "Fake reviews on e-commerce platforms mislead millions of buyers every day!",
        "description": (
            "Paid review farms manipulate product ratings on Amazon, Flipkart, and other "
            "platforms. Consumers can't distinguish genuine from fake reviews. An AI-powered "
            "review authenticity checker could protect buyers."
        ),
        "category": "Technology",
    },
    {
        "title": "Digital payments fail silently — money debited but not credited, and nobody helps!",
        "description": (
            "UPI and wallet transactions fail frequently with money stuck in limbo for days. "
            "Customer support is automated and unhelpful. A real-time payment resolution "
            "dashboard with auto-escalation could save users immense frustration."
        ),
        "category": "Technology",
    },

    # ── Employment (12) ──────────────────────────────────────────────
    {
        "title": "Why do job portals show 500 'relevant' results that are all completely irrelevant?",
        "description": (
            "Naukri, Indeed, and LinkedIn job searches return poorly matched results. "
            "Candidates waste hours applying to jobs they won't get. AI-powered skill-based "
            "matching rather than keyword matching could fix job discovery."
        ),
        "category": "Employment",
    },
    {
        "title": "Gig workers have zero benefits — no insurance, no sick leave, no minimum wage!",
        "description": (
            "Delivery riders, cleaners, and drivers work 12-hour days with no social security. "
            "Platforms classify them as 'partners' to avoid employer obligations. A portable "
            "benefits platform for gig workers is desperately needed."
        ),
        "category": "Employment",
    },
    {
        "title": "Hiring domestic help is based on trust and luck — there's no verification system!",
        "description": (
            "Millions of urban Indians hire maids, cooks, and nannies through word-of-mouth. "
            "There's no background verification, no contracts, and no recourse. A verified "
            "domestic worker platform could build trust on both sides."
        ),
        "category": "Employment",
    },
    {
        "title": "Engineering graduates drive Ola because their degree taught them nothing useful!",
        "description": (
            "India produces 1.5 million engineers annually but most are unemployable because "
            "curricula don't match industry needs. A skilling-to-placement pipeline that "
            "partners with employers could fix this massive mismatch."
        ),
        "category": "Employment",
    },
    {
        "title": "Government job aspirants waste 5-7 years preparing — most never get selected!",
        "description": (
            "Crores of youth prepare for UPSC, SSC, and state exams for years with low "
            "success rates. No guidance system helps them assess realistic chances or "
            "explore alternatives. Career diversification tools are needed."
        ),
        "category": "Employment",
    },
    {
        "title": "Freelancers in India get paid 70%% less than global rates for the same work!",
        "description": (
            "Indian freelancers on Upwork and Fiverr face geographic rate discrimination. "
            "Clients expect 'India pricing' regardless of quality. A platform that enforces "
            "skill-based pricing could create fairer markets."
        ),
        "category": "Employment",
    },
    {
        "title": "Blue-collar workers can't find daily-wage jobs without standing at a naka every morning!",
        "description": (
            "Construction labourers, painters, and plumbers gather at street corners hoping "
            "someone hires them. It's undignified and inefficient. A mobile-first daily-work "
            "matching platform could formalise this massive market."
        ),
        "category": "Employment",
    },
    {
        "title": "Women re-entering the workforce after maternity face invisible discrimination!",
        "description": (
            "Career breaks for motherhood result in skills perception gaps. Recruiters reject "
            "women with gaps on their resumes. Return-to-work programmes exist but are rare. "
            "A specialised job platform for career returnees could help."
        ),
        "category": "Employment",
    },
    {
        "title": "Internship stipends are insultingly low or zero — students work for free and learn nothing!",
        "description": (
            "Indian companies treat interns as free labour. Students need internships for "
            "placements but get exploited. A marketplace ensuring minimum stipends and "
            "learning outcomes could professionalise internships."
        ),
        "category": "Employment",
    },
    {
        "title": "Interview processes are broken — 7 rounds for a junior developer position? Seriously?",
        "description": (
            "Tech hiring in India has become absurdly long with multiple redundant rounds. "
            "Candidates drop out and companies lose talent. Standardised skill assessments "
            "accepted across companies could simplify hiring."
        ),
        "category": "Employment",
    },
    {
        "title": "Salary negotiation is a black box — employees have no idea what others earn!",
        "description": (
            "Pay transparency is non-existent in India. Employees accept lowball offers "
            "because they can't benchmark. An anonymous salary-sharing platform by role, "
            "company, and location could empower millions of workers."
        ),
        "category": "Employment",
    },
    {
        "title": "Skilled migrants from Bihar and UP face exploitation in destination cities!",
        "description": (
            "Internal migrant workers face wage theft, terrible housing, and social "
            "discrimination. They have no support network in new cities. A migrant worker "
            "support platform with legal aid and community could help."
        ),
        "category": "Employment",
    },
]


# ======================================================================
# Public accessors
# ======================================================================

def get_seed_problems() -> List[Dict[str, str]]:
    """Return the full list of seed problem dicts."""
    return list(SEED_PROBLEMS)


# ======================================================================
# Database seeding
# ======================================================================

def seed_database(db_path: str) -> None:
    """Process every seed problem through :class:`NLPEngine` and
    insert the results into the SQLite database at *db_path*.

    Uses models.py's init_db and insert_problem to ensure schema
    consistency with the Flask application.

    Parameters
    ----------
    db_path : str
        Filesystem path to the target SQLite database file.
    """
    from nlp_engine import NLPEngine
    from models import init_db, get_db, insert_problem

    engine = NLPEngine()
    problems = get_seed_problems()

    # Ensure tables exist via models.py schema
    init_db(db_path)

    conn = get_db(db_path)
    total = len(problems)
    print("[seed_database] Processing %d problems ..." % total)

    for idx, prob in enumerate(problems, start=1):
        combined_text = prob["title"] + " " + prob["description"]
        result = engine.analyze_problem(combined_text, category=prob["category"])

        problem_data = {
            "title": prob["title"],
            "description": prob["description"],
            "category": prob["category"],
            "frustration_score": result.get("frustration_score", 0),
            "market_size_score": result.get("market_score", 0),
            "solvability_score": result.get("solvability_score", 0),
            "overall_score": result.get("overall_score", 0),
            "root_cause": result.get("root_cause", ""),
            "inefficiency": json.dumps(result.get("inefficiencies", [])),
            "sentiment": result.get("sentiment", 0),
            "keyword_tags": result.get("keywords", []),
            "source": "curated",
        }

        insert_problem(conn, problem_data)

        # Progress feedback (ASCII only for Windows console)
        if idx % 10 == 0 or idx == total:
            pct = idx / total * 100
            title_preview = prob["title"][:55]
            print("  [%3d/%d] %5.1f%%  %s..." % (idx, total, pct, title_preview))

    conn.commit()
    conn.close()
    print("[seed_database] Done. %d problems inserted into '%s'." % (total, db_path))


# ----------------------------------------------------------------------
# CLI entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    db = sys.argv[1] if len(sys.argv) > 1 else "fixmyitch.db"
    seed_database(db)
