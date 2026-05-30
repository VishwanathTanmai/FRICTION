import json
from nlp_engine import NLPEngine
from models import get_db, insert_problem

EXTRA_PROBLEMS = [
    {
        "title": "Why is it so hard to find reliable maids and cooks in tier-1 cities without paying exorbitant agency fees?",
        "description": "The current system relies on word of mouth which is slow and unreliable. Agencies charge thousands just for a contact number, and there's no background verification or standard pricing.",
        "category": "Housing"
    },
    {
        "title": "Booking a tatkal train ticket on IRCTC is a nightmare that forces people to use illegal touts.",
        "description": "The site always crashes at 10 AM, and by the time you login, tickets are waitlisted. Meanwhile, touts with automated scripts book tickets and sell them at a massive premium. It's frustrating and unfair.",
        "category": "Transport"
    },
    {
        "title": "Small business owners struggle to navigate GST filing because the portal is confusing and requires a CA for even simple returns.",
        "description": "Instead of making it easy to pay taxes, the complicated interface and constant glitches force small shopkeepers to spend thousands on accountants. It's too complex for common people.",
        "category": "Finance"
    },
    {
        "title": "There is no standardized platform to check the real background and reviews of driving schools.",
        "description": "Most driving schools just teach you how to pass the test, not how to drive safely in traffic. Instructors are often rude and cars are in bad condition, but you only find out after paying.",
        "category": "Education"
    },
    {
        "title": "Finding a clean, hygienic public restroom in Indian cities is practically impossible.",
        "description": "Even in commercial hubs, public toilets are a nightmare. People would willingly pay a small fee for guaranteed clean, safe restrooms, especially women.",
        "category": "Health"
    },
    {
        "title": "Why do gyms trap you into yearly memberships and make it impossible to cancel or transfer?",
        "description": "Gyms use high-pressure sales tactics to lock you in for a year. If you relocate or get injured, your money is gone. There's zero flexibility and toxic business practices.",
        "category": "Health"
    },
    {
        "title": "Getting a refund for a failed UPI transaction takes days of follow-ups and anxiety.",
        "description": "When money is deducted but not credited, banks blame the app, and the app blames the bank. There's no single point of contact and customer support is just an automated bot.",
        "category": "Finance"
    },
    {
        "title": "Street food vendors want to accept online orders but Swiggy/Zomato take 30% commission which kills their margin.",
        "description": "Local vendors operate on thin margins. The duopoly of food delivery apps extracts too much value, making it unviable for small hawkers to go digital.",
        "category": "Food"
    },
    {
        "title": "Finding verified, non-scammy packers and movers is a gamble.",
        "description": "Many companies hold your luggage hostage mid-transit demanding more money. Reviews are often fake, and there is no accountability if items are broken or stolen.",
        "category": "Logistics"
    },
    {
        "title": "There's no reliable way to recycle electronic waste from homes; it just goes into regular trash.",
        "description": "People want to dispose of old phones and cables responsibly, but finding an e-waste drop-off point is too much effort. Scrap dealers don't handle it safely.",
        "category": "Environment"
    },
    {
        "title": "Why is customer support for broadband/internet providers so disconnected from the ground reality?",
        "description": "When the internet goes down, the app says 'all systems fine'. You have to tweet at them to get any real response. The technicians are underpaid and overworked.",
        "category": "Technology"
    },
    {
        "title": "College curriculums for software engineering are outdated and don't teach modern tools like Git or Cloud.",
        "description": "Students graduate knowing theoretical algorithms but don't know how to deploy a basic web app. The gap between academia and industry expectations is huge.",
        "category": "Education"
    },
    {
        "title": "Claiming medical insurance is an incredibly stressful process designed to find reasons to reject your claim.",
        "description": "Patients' families have to run around getting stamps and signatures while dealing with a health crisis. Insurance companies use confusing loopholes to deny coverage.",
        "category": "Finance"
    },
    {
        "title": "The process of getting a passport police verification still involves implicit bribery in many areas.",
        "description": "Despite digitalization, the final police verification step is opaque. Cops often hint at 'chai paani' to process the file quickly, and there's no way to report it without risking delays.",
        "category": "Governance"
    },
    {
        "title": "Farmers lack direct access to consumers and are forced to sell to middlemen at throwaway prices.",
        "description": "While consumers pay premium prices for vegetables in cities, the farmer barely covers transportation costs. The APMC mandi system is heavily monopolized.",
        "category": "Agriculture"
    },
    {
        "title": "Fast-fashion brands use cheap materials that get ruined in one wash, creating massive textile waste.",
        "description": "Clothes are treated as disposable. There's no accessible infrastructure for repairing or upcycling clothes, leading to tons of garments ending up in landfills.",
        "category": "Environment"
    },
    {
        "title": "Freelancers struggle to get paid on time because clients delay invoices indefinitely.",
        "description": "There is no legal protection or escrow system for independent workers. Agencies delay payments by 90 days, causing massive cash flow problems for individuals.",
        "category": "Employment"
    },
    {
        "title": "Why are movie theater snacks absurdly overpriced with no outside food allowed?",
        "description": "A popcorn combo costs more than the movie ticket itself. It feels like an exploitative monopoly, especially for families with kids.",
        "category": "Food"
    },
    {
        "title": "Traffic police fines are sometimes arbitrary, and contesting a wrong challan is a bureaucratic nightmare.",
        "description": "Cameras capture wrong number plates, or cops issue fines without proof. Challenging it requires visiting courts, so people just pay the fine out of frustration.",
        "category": "Transport"
    },
    {
        "title": "It's nearly impossible to find reliable day-care or creches for working mothers in corporate areas.",
        "description": "Nuclear families struggle because quality day-care is either absent or wildly expensive. This forces many women to drop out of the workforce entirely.",
        "category": "Housing"
    }
]

def add_extra_data(db_path="fixmyitch.db"):
    engine = NLPEngine()
    conn = get_db(db_path)
    
    print(f"Adding {len(EXTRA_PROBLEMS)} new problems...")
    
    count = 0
    for prob in EXTRA_PROBLEMS:
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
            "source": "extra",
        }

        insert_problem(conn, problem_data)
        count += 1
        print(f"Added: {prob['title'][:50]}...")
        
    conn.commit()
    conn.close()
    print(f"\nSuccessfully added {count} more problems to the database.")

if __name__ == "__main__":
    add_extra_data()
