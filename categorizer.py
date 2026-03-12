def get_txn_prefix(transaction_id):
    txn = str(transaction_id).upper().strip()

    if txn.startswith("UPI"):
        return "UPI"
    elif txn.startswith("NEFT"):
        return "NEFT"
    elif txn.startswith("IMPS"):
        return "IMPS"
    elif txn.startswith("CARD"):
        return "CARD"
    else:
        return "TXN"

def categorize_by_description(description):
    desc = str(description).lower()

    if any(word in desc for word in [
        "swiggy", "zomato", "restaurant", "cafe", "food", "blinkit",
        "dominos", "mcdonald", "kfc", "pizza", "burger", "hotel",
        "bakery", "dining", "eat", "kitchen", "biryani", "canteen"
    ]):
        return "Food"

    elif any(word in desc for word in [
        "amazon", "flipkart", "myntra", "meesho", "ajio", "nykaa",
        "snapdeal", "shopping", "mart", "store", "purchase", "buy",
        "mall", "retail", "bigbasket", "grofer", "dmart"
    ]):
        return "Shopping"

    elif any(word in desc for word in [
        "netflix", "spotify", "prime", "hotstar", "youtube", "zee5",
        "sonyliv", "subscription", "entertainment", "movie", "cinema",
        "pvr", "inox", "bookmyshow", "gaming", "steam"
    ]):
        return "Entertainment"

    elif any(word in desc for word in [
        "uber", "ola", "irctc", "makemytrip", "redbus", "yatra",
        "cleartrip", "airline", "flight", "train", "bus", "travel",
        "rapido", "cab", "auto", "metro", "toll", "fuel", "petrol"
    ]):
        return "Travel"

    elif any(word in desc for word in [
        "rent", "landlord", "housing", "lease", "pg ", "hostel"
    ]):
        return "Rent"

    elif any(word in desc for word in [
        "electricity", "water", "gas", "broadband", "airtel", "jio",
        "bsnl", "vi ", "vodafone", "idea", "recharge", "bill", "utility",
        "tata power", "bescom", "mseb", "internet", "wifi"
    ]):
        return "Utilities"

    elif any(word in desc for word in [
        "hospital", "pharmacy", "medical", "doctor", "apollo", "1mg",
        "netmeds", "pharmeasy", "clinic", "health", "dental", "lab",
        "diagnostic", "medicine", "chemist"
    ]):
        return "Healthcare"

    elif any(word in desc for word in [
        "school", "college", "university", "course", "udemy", "coursera",
        "fees", "tuition", "education", "book", "stationery", "byju"
    ]):
        return "Education"

    elif any(word in desc for word in [
        "salary", "sal cr", "neft cr", "income", "interest cr",
        "dividend", "bonus", "stipend", "credit by", "refund"
    ]):
        return "Income"

    elif any(word in desc for word in [
        "emi", "loan", "mortgage", "insurance", "lic", "sip",
        "mutual fund", "investment", "fd ", "ppf", "nps"
    ]):
        return "Finance & Investment"

    else:
        return "Miscellaneous"


def categorize(transaction_id, description):
    prefix = get_txn_prefix(transaction_id)
    desc   = str(description).lower()

    if prefix == "NEFT":
        if any(w in desc for w in ["salary", "sal cr", "income", "bonus", "stipend"]):
            return "Income"
        elif any(w in desc for w in ["rent", "landlord", "housing", "lease"]):
            return "Rent"
        elif any(w in desc for w in ["refund", "reversal", "cashback"]):
            return "Income"
        elif any(w in desc for w in ["emi", "loan", "insurance", "lic", "sip", "mutual fund"]):
            return "Finance & Investment"
        else:
            return "Income"   

    elif prefix == "IMPS":
        if any(w in desc for w in ["rent", "landlord", "housing", "lease", "pg ", "hostel"]):
            return "Rent"
        elif any(w in desc for w in ["salary", "freelance", "stipend", "income"]):
            return "Income"
        else:
            return "Income"  

    elif prefix == "CARD":
        if any(w in desc for w in ["netflix", "spotify", "prime", "hotstar", "youtube",
                                    "zee5", "sonyliv", "subscription", "bookmyshow",
                                    "pvr", "inox", "gaming", "steam"]):
            return "Entertainment"
        elif any(w in desc for w in ["amazon", "flipkart", "myntra", "meesho", "ajio",
                                      "nykaa", "snapdeal", "shopping", "mall", "retail",
                                      "store", "purchase", "buy", "dmart"]):
            return "Shopping"
        elif any(w in desc for w in ["swiggy", "zomato", "restaurant", "cafe", "food",
                                      "dominos", "mcdonald", "kfc", "pizza", "burger",
                                      "bakery", "dining", "biryani"]):
            return "Food"
        elif any(w in desc for w in ["electricity", "water", "gas", "broadband", "airtel",
                                      "jio", "recharge", "bill", "utility", "internet"]):
            return "Utilities"
        else:
            return "Shopping"   # card payments default to shopping

    # UPI & TXN — fully rely on description keywords
    else:
        return categorize_by_description(description)