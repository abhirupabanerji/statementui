def get_txn_prefix(transaction_id):
    txn = str(transaction_id).upper().strip()

    if "UPI" in txn:
        return "UPI"
    elif "NEFT" in txn:
        return "NEFT"
    elif "IMPS" in txn:
        return "IMPS"
    elif "CARD" in txn or "POS" in txn:
        return "CARD"
    else:
        return "TXN"


# ---------------- DESCRIPTION BASED ----------------
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
        "netmeds", "pharmeasy", "clinic", "health"
    ]):
        return "Healthcare"

    elif any(word in desc for word in [
        "school", "college", "course", "fees", "tuition", "education"
    ]):
        return "Education"

    elif any(word in desc for word in [
        "salary", "income", "interest", "dividend", "bonus", "stipend",
        "refund", "cashback"
    ]):
        return "Income"

    elif any(word in desc for word in [
        "emi", "loan", "insurance", "lic", "sip",
        "mutual fund", "investment"
    ]):
        return "Finance & Investment"

    else:
        return "Miscellaneous"


# ---------------- MAIN CATEGORIZATION ----------------
def categorize(transaction_id, description):
    prefix = get_txn_prefix(transaction_id)
    desc = str(description).lower()

    # -------- NEFT --------
    if prefix == "NEFT":
        if any(w in desc for w in ["salary", "income", "bonus", "stipend", "refund"]):
            return "Income"
        elif any(w in desc for w in ["rent", "lease"]):
            return "Rent"
        elif any(w in desc for w in ["emi", "loan", "insurance"]):
            return "Finance & Investment"
        else:
            return "Bank Transfer"   # ✅ FIXED (was always Income)

    # -------- IMPS --------
    elif prefix == "IMPS":
        if any(w in desc for w in ["rent", "lease", "pg", "hostel"]):
            return "Rent"
        elif any(w in desc for w in ["salary", "income", "freelance", "stipend"]):
            return "Income"
        else:
            return "Transfer"   # ✅ FIXED (important)

    # -------- CARD --------
    elif prefix == "CARD":
        return categorize_by_description(description)   # ✅ cleaner logic

    # -------- UPI / OTHERS --------
    else:
        return categorize_by_description(description)
