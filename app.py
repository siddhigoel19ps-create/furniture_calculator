# =============================================================================
# Heritage Oak Furniture Studio - Furniture Cost Calculator (Version 2)
# Course : Python Programming for Business Students (End-Term Project)
# Tools : Python + Streamlit (no external database)
#
# What this app does:
# A customer picks furniture, material, size, quantity, delivery, etc.
# The app calculates an estimated bill, shows a cost breakdown, tracks the
# discount and the customer's budget, and lets them download a quote.
#
# Run it with:  python3 -m streamlit run app.py
# =============================================================================

import streamlit as st

# -----------------------------------------------------------------------------
# 1. PAGE SETTINGS (must be the first Streamlit command in the file)
# -----------------------------------------------------------------------------
st.set_page_config(
  page_title="Heritage Oak Furniture Studio",
  layout="wide",
)

# -----------------------------------------------------------------------------
# 2. PRICE LIST AND BUSINESS RULES (all pricing assumptions live here)
# -----------------------------------------------------------------------------
# Dictionary: furniture category -> base price per item (in Indian rupees).
FURNITURE_PRICES = {
  "Sofa": 25000,
  "Bed": 30000,
  "Dining Table": 22000,
  "Wardrobe": 28000,
  "Study Table": 9000,
}

# Dictionaries used only for the look of the app (emoji and colours)
CATEGORY_ICONS = {name: "" for name in FURNITURE_PRICES}
MATERIAL_COLORS = {
  "Engineered Wood": "#D9B98A",
  "Solid Wood": "#8B5A2B",
  "Metal": "#9FB0BC",
}

# Fixed charges (assumptions for this project)
CUSTOMIZATION_CHARGE_PER_ITEM = 1500  # Rs per item if customization is chosen
STANDARD_DELIVERY_CHARGE = 1500    # Rs per order
EXPRESS_DELIVERY_CHARGE = 3000     # Rs per order
PREMIUM_EXTRA_DISCOUNT = 5       # extra % discount for Premium customers

# Estimated delivery time (assumption, shown to the customer)
DELIVERY_DAYS = {"Standard": "7-10 days", "Express": "2-3 days"}

# Discount slabs: if the goods value reaches the limit, this % discount is given
SLAB_LOW, SLAB_MID, SLAB_HIGH = 40000, 75000, 150000
RATE_LOW, RATE_MID, RATE_HIGH = 5, 7, 10

# Limits used for input validation
MIN_QUANTITY = 1
MAX_QUANTITY = 50

# Default values of every input (also used by the Reset button)
DEFAULTS = {
  "category": "Sofa",
  "material": "Engineered Wood",
  "size": "Medium",
  "quantity": 1,
  "customization": False,
  "delivery": "Standard",
  "customer_type": "Regular",
  "budget": 100000,
}

# Ready-made orders for the "Quick start" buttons (each is a full set of inputs)
PRESETS = {
  "Cozy Living Room": {
    "category": "Sofa", "material": "Solid Wood", "size": "Large",
    "quantity": 2, "customization": False, "delivery": "Standard",
    "customer_type": "Regular", "budget": 150000,
  },
  "Bedroom Upgrade": {
    "category": "Bed", "material": "Solid Wood", "size": "Large",
    "quantity": 1, "customization": True, "delivery": "Express",
    "customer_type": "Premium", "budget": 100000,
  },
  "Student Study Setup": {
    "category": "Study Table", "material": "Engineered Wood", "size": "Small",
    "quantity": 1, "customization": False, "delivery": "Standard",
    "customer_type": "Regular", "budget": 20000,
  },
}


# Three named designs for each furniture category. These are visual choices;
# the original category-based price calculation remains unchanged.
PRODUCT_DESIGNS = {
  "Sofa": [
    ("The Alder Lounge", "Contemporary 3-seater", "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=900&q=85"),
    ("The Camden Curve", "Soft, rounded statement sofa", "https://images.unsplash.com/photo-1550254478-ead4f891c7f?auto=format&fit=crop&w=900&q=85"),
    ("The Rowan Classic", "Timeless tailored sofa", "https://images.unsplash.com/photo-1550254478-ead4f891c7f?auto=format&fit=crop&w=900&q=85"),
  ],
  "Bed": [
    ("The Haven Bed", "Warm upholstered headboard", "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=85"),
    ("The Solstice Frame", "Minimal natural-wood frame", "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=900&q=85"),
    ("The Willow Retreat", "Soft, relaxed bedroom style", "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=900&q=85"),
  ],
  "Dining Table": [
    ("The Gather Table", "Classic family dining table", "https://images.unsplash.com/photo-1617806118233-18e1de247200?auto=format&fit=crop&w=900&q=85"),
    ("The Arden Dining Set", "Modern clean-lined design", "https://images.unsplash.com/photo-1604578762246-41134e37f9cc?auto=format&fit=crop&w=900&q=85"),
    ("The Oakridge Table", "Natural wood dining style", "https://images.unsplash.com/photo-1617104678098-de229db51175?auto=format&fit=crop&w=900&q=85"),
  ],
  "Wardrobe": [
    ("The Elara Wardrobe", "Elegant full-height storage", "https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&w=900&q=85"),
    ("The Linden Closet", "Minimal built-in look", "https://images.unsplash.com/photo-1558997510-83ea9252edf8?auto=format&fit=crop&w=900&q=85"),
    ("The Sora Wardrobe", "Warm contemporary finish", "https://images.unsplash.com/photo-1595514535415-dae9e2f5f6f3?auto=format&fit=crop&w=900&q=85"),
  ],
  "Study Table": [
    ("The Focus Desk", "Simple everyday workstation", "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=900&q=85"),
    ("The Atelier Desk", "Modern creative workspace", "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?auto=format&fit=crop&w=900&q=85"),
    ("The Scholar Table", "Compact study-room design", "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?auto=format&fit=crop&w=900&q=85"),
  ],
}


# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def format_rupees(amount):
  """Convert a number into Indian rupee format, e.g. 150000 -> ₹1,50,000."""
  # Remember the sign, then work with a positive whole number
  sign = ""
  if amount < 0:
    sign = "- "
    amount = -amount
  digits = str(round(amount))

  # Indian style: last 3 digits together, then groups of 2 digits
  if len(digits) <= 3:
    return sign + "₹" + digits
  last_three = digits[-3:]
  remaining = digits[:-3]
  groups = []           # a list that will hold the 2-digit groups
  while len(remaining) > 2:
    groups.insert(0, remaining[-2:])  # add the group at the front
    remaining = remaining[:-2]
  if remaining != "":
    groups.insert(0, remaining)
  groups.append(last_three)
  return sign + "₹" + ",".join(groups)


def calculate_bill(category, material, size, quantity,
          wants_customization, delivery, customer_type):
  """Calculate the full furniture bill and return all the numbers in a dictionary.

  Raises ValueError with a friendly message if any input is invalid.
  """
  # ---- Step 1: Validate the inputs so the app never crashes ----
  if category not in FURNITURE_PRICES:
    raise ValueError("Please select a valid furniture category.")

  try:
    quantity = int(quantity)       # make sure quantity is a whole number
  except (TypeError, ValueError):
    raise ValueError("Quantity must be a whole number.")

  if quantity < MIN_QUANTITY:
    raise ValueError("Quantity must be at least 1. Zero or negative is not allowed.")
  if quantity > MAX_QUANTITY:
    raise ValueError("For more than 50 items, please contact our store for a bulk quote.")

  # ---- Step 2: Base price from the dictionary ----
  base_price = FURNITURE_PRICES[category]

  # ---- Step 3: Material adjustment (percentage of the base price) ----
  if material == "Engineered Wood":
    material_adjustment = 0             # standard material
  elif material == "Solid Wood":
    material_adjustment = round(base_price * 0.30)  # +30%
  elif material == "Metal":
    material_adjustment = round(base_price * 0.10)  # +10%
  else:
    raise ValueError("Please select a valid material.")

  # ---- Step 4: Size adjustment (percentage of the base price) ----
  if size == "Small":
    size_adjustment = -round(base_price * 0.10)   # -10% (less material used)
  elif size == "Medium":
    size_adjustment = 0               # standard size
  elif size == "Large":
    size_adjustment = round(base_price * 0.25)    # +25%
  else:
    raise ValueError("Please select a valid size.")

  # ---- Step 5: Price of ONE item and total for all items ----
  price_per_item = base_price + material_adjustment + size_adjustment
  furniture_total = price_per_item * quantity

  # ---- Step 6: Customization charges (bool: True / False from the checkbox) ----
  if wants_customization:
    customization_charges = CUSTOMIZATION_CHARGE_PER_ITEM * quantity
  else:
    customization_charges = 0

  # Value of the goods (used to decide the discount, delivery is NOT discounted)
  goods_total = furniture_total + customization_charges

  # ---- Step 7: Delivery charges ----
  if delivery == "Standard":
    delivery_charges = STANDARD_DELIVERY_CHARGE
  elif delivery == "Express":
    delivery_charges = EXPRESS_DELIVERY_CHARGE
  else:
    raise ValueError("Please select a valid delivery option.")

  # ---- Step 8: Subtotal (formula given in the project brief) ----
  subtotal = goods_total + delivery_charges

  # ---- Step 9: Discount rule ----
  # Rule A: bigger orders get a bigger discount (based on goods_total)
  if goods_total >= SLAB_HIGH:
    discount_percent = RATE_HIGH
  elif goods_total >= SLAB_MID:
    discount_percent = RATE_MID
  elif goods_total >= SLAB_LOW:
    discount_percent = RATE_LOW
  else:
    discount_percent = 0

  # Rule B: Premium customers get an extra discount
  if customer_type == "Premium":
    discount_percent = discount_percent + PREMIUM_EXTRA_DISCOUNT
  elif customer_type != "Regular":
    raise ValueError("Please select a valid customer type.")

  discount_amount = round(goods_total * discount_percent / 100)

  # ---- Step 10: Final bill (max() makes sure it can never be negative) ----
  final_bill = max(subtotal - discount_amount, 0)

  # Send all results back together in one dictionary
  return {
    "base_price": base_price,
    "material_adjustment": material_adjustment,
    "size_adjustment": size_adjustment,
    "price_per_item": price_per_item,
    "quantity": quantity,
    "furniture_total": furniture_total,
    "customization_charges": customization_charges,
    "goods_total": goods_total,
    "delivery_charges": delivery_charges,
    "subtotal": subtotal,
    "discount_percent": discount_percent,
    "discount_amount": discount_amount,
    "final_bill": final_bill,
  }


def get_next_discount_goal(goods_total):
  """Return (goods value needed, discount %) for the NEXT discount slab.

  Returns (None, None) if the customer already has the highest slab.
  """
  if goods_total < SLAB_LOW:
    return SLAB_LOW, RATE_LOW
  elif goods_total < SLAB_MID:
    return SLAB_MID, RATE_MID
  elif goods_total < SLAB_HIGH:
    return SLAB_HIGH, RATE_HIGH
  else:
    return None, None


def category_label(name):
  """Show an emoji next to each furniture category name."""
  return name


def reset_form():
  """Put every input back to its default value (used by the Reset button)."""
  for key, value in DEFAULTS.items():
    st.session_state[key] = value
  st.toast("Everything has been reset.")


def load_preset(preset_name):
  """Fill all inputs with a ready-made order (used by the Quick start buttons)."""
  for key, value in PRESETS[preset_name].items():
    st.session_state[key] = value
  st.toast("Loaded: " + preset_name)


# -----------------------------------------------------------------------------
# 4. STYLING (CSS = the colours and look: beige, white, brown + butter yellow/blue)
# -----------------------------------------------------------------------------
st.markdown(
  """
  <style>
  :root { color-scheme: light; }
  .stApp { background: #F4F0E7; color: #29372D; }
  [data-testid="stWidgetLabel"] p, .stMarkdown p, .stMarkdown li,
  h1, h2, h3, h4, label { color: #29372D !important; }
  [data-testid="stHeader"] { background: rgba(244,240,231,.92); }
  .block-container { max-width: 1400px; padding-top: 2rem; }
  .st-key-card_furniture, .st-key-card_extras, .st-key-card_customer,
  .st-key-card_results {
    background: #FBF9F4; border: 1px solid #D8D1C2 !important;
    border-radius: 16px; box-shadow: 0 5px 18px rgba(41,55,45,.06);
  }
  div[data-baseweb="select"] > div, div[data-baseweb="input"],
  div[data-baseweb="textarea"] { background: #FFFEFA !important; border-radius: 9px !important; }
  .stButton > button, .stDownloadButton > button {
    background: #344638; color: #FAF8F2; border: 1px solid #344638;
    border-radius: 8px; font-weight: 600; transition: .2s ease;
  }
  .stButton > button:hover, .stDownloadButton > button:hover {
    background: #526B55; color: white; border-color: #526B55; transform: translateY(-1px);
  }
  .hero {
    background: linear-gradient(90deg, rgba(25,38,29,.86), rgba(45,62,46,.58)),
    url('https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1800&q=85') center/cover;
    border-radius: 18px; min-height: 310px; padding: 72px 32px 54px;
    text-align: left; box-shadow: 0 10px 28px rgba(41,55,45,.15);
  }
  .hero-title { color: #FAF8F2; font-size: clamp(2rem,4vw,3.4rem); font-weight: 750; letter-spacing: -.03em; }
  .hero-sub { color: #EEE9DC; font-size: 1.12rem; margin-top: 12px; max-width: 650px; }
  .eyebrow { color: #A3A17D; text-transform: uppercase; letter-spacing: .18em; font-size: .78rem; font-weight: 700; }
  .section-intro { color: #687365; margin-top: -8px; }
  .product-card { background: #FBF9F4; border: 1px solid #DED8CA; border-radius: 13px; overflow: hidden; height: 100%; }
  .product-card img { width: 100%; height: 175px; object-fit: cover; display: block; }
  .product-copy { padding: 13px 15px 16px; }
  .product-name { color: #29372D; font-weight: 700; font-size: 1.05rem; }
  .product-price { color: #687365; font-size: .9rem; margin-top: 4px; }
  .step-card, .review-card { background: #FBF9F4; border: 1px solid #DED8CA; border-radius: 12px; padding: 18px; height: 100%; }
  .step-number { color: #8B9678; font-size: .78rem; font-weight: 800; letter-spacing: .12em; }
  .step-title { color: #29372D; font-weight: 700; margin: 7px 0; }
  .review-stars { color: #A17C45; letter-spacing: .12em; }
  .preview-card { background: #E9E6DA; border: 1px solid #D6D0C0; border-radius: 14px; padding: 14px 18px; margin-bottom: 14px; }
  .preview-icon { display: none; }
  .preview-title { font-size: 1.2rem; font-weight: 700; color: #29372D; }
  .chip { display:inline-block; padding:5px 10px; border-radius:20px; font-size:.82rem; margin:3px; background:#E3E6DA; color:#344638; }
  .chip-yellow, .chip-blue, .chip-beige { background:#E3E6DA; color:#344638; }
  .swatch { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:5px; }
  .bill-box { background: linear-gradient(135deg,#29372D,#435A45); border-radius:15px; padding:24px; text-align:center; margin:8px 0 14px; }
  .bill-label { color:#E4E8DC; letter-spacing:2px; font-size:.8rem; }
  .bill-amount { color:#E8D9B8; font-size:2.7rem; font-weight:800; }
  .bill-note { color:#E4E8DC; font-size:.9rem; }
  .bar-row { display:flex; align-items:center; gap:10px; margin:10px 0; color:#29372D; }
  .bar-label { width:130px; font-size:.9rem; }
  .bar-track { flex:1; background:#E3E0D5; border-radius:99px; height:12px; overflow:hidden; }
  .bar-fill { height:100%; border-radius:99px; }
  .fill-brown { background:#526B55; } .fill-yellow { background:#A3A17D; } .fill-blue { background:#B08B61; }
  .bar-value { width:100px; text-align:right; font-weight:700; }
  </style>
  """,
  unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 5. STORE HEADER AND WELCOME MESSAGE
# -----------------------------------------------------------------------------
st.markdown(
  """
<div class="hero">
 <div class="eyebrow">Thoughtfully made · Naturally timeless</div>
 <div class="hero-title">Heritage Oak Furniture Studio</div>
 <div class="hero-sub">Furniture with character. Spaces with warmth. Explore our collection and create a transparent estimate for your home.</div>
</div>
  """,
  unsafe_allow_html=True,
)
st.write("")
st.markdown("### Furniture for considered living")
st.markdown('<p class="section-intro">Explore our essential pieces, crafted to bring comfort and natural character into your space.</p>', unsafe_allow_html=True)
products = [
  ("Sofa", "₹25,000 onwards", "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=900&q=85"),
  ("Bed", "₹30,000 onwards", "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=85"),
  ("Dining Table", "₹22,000 onwards", "https://images.unsplash.com/photo-1617806118233-18e1de247200?auto=format&fit=crop&w=900&q=85"),
  ("Wardrobe", "₹28,000 onwards", "https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&w=900&q=85"),
  ("Study Table", "₹9,000 onwards", "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=900&q=85"),
]
# Use verified-format Unsplash image URLs for all cards; image failures fall back to a neutral card.
products[2] = ("Dining Table", "₹22,000 onwards", "https://images.unsplash.com/photo-1617806118233-18e1de247200?auto=format&fit=crop&w=900&q=85")
products[4] = ("Study Table", "₹9,000 onwards", "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=900&q=85")
product_cols = st.columns(5, gap="medium")
for col, (name, price, image_url) in zip(product_cols, products):
  with col:
    st.markdown(f'<div class="product-card"><img src="{image_url}" alt="{name} furniture"><div class="product-copy"><div class="product-name">{name}</div><div class="product-price">{price}</div></div></div>', unsafe_allow_html=True)
st.write("")
st.markdown("### A little more about our approach")
st.markdown('<p class="section-intro">We make it easier to plan your furniture purchase with clear pricing, flexible choices and an estimate that updates as you build your order.</p>', unsafe_allow_html=True)
review_cols = st.columns(2, gap="medium")
with review_cols[0]:
  st.markdown('<div class="review-card"><div class="eyebrow">Sample review layout · Not a real testimonial</div><div class="review-stars"></div><b>“Thoughtful design and clear pricing.”</b><p>This is placeholder text to demonstrate how customer feedback will appear. Replace it with a genuine customer review after receiving permission.</p><small>Customer name to be added with permission</small></div>', unsafe_allow_html=True)
with review_cols[1]:
  st.markdown('<div class="review-card"><div class="eyebrow">Sample review layout · Not a real testimonial</div><div class="review-stars"></div><b>“A simple way to plan a furniture order.”</b><p>This is placeholder text only, not an actual customer review. Add verified feedback here when available.</p><small>Customer name to be added with permission</small></div>', unsafe_allow_html=True)
st.divider()
st.markdown("## Build your furniture estimate")
st.markdown('<p class="section-intro">Choose a furniture category, browse three named designs with photos, and build your estimate. Your itemized total updates automatically.</p>', unsafe_allow_html=True)

# Give every input its starting value the first time the page opens
for key, value in DEFAULTS.items():
  if key not in st.session_state:
    st.session_state[key] = value

# -----------------------------------------------------------------------------
# 6. QUICK START BUTTONS (each button fills in a full order in one click)
# -----------------------------------------------------------------------------
st.markdown("** Quick start ideas**")
preset_names = list(PRESETS.keys())       # a list of the button names
preset_columns = st.columns(4)
for position in range(len(preset_names)):    # loop over the 3 preset buttons
  with preset_columns[position]:
    st.button(
      preset_names[position],
      on_click=load_preset,
      args=(preset_names[position],),
      key="preset_button_" + str(position),
    )
with preset_columns[3]:
  st.button(" Reset / Start over", on_click=reset_form)

st.write("")

# Two columns: inputs on the left, results on the right
left_column, right_column = st.columns(2, gap="large")

# -----------------------------------------------------------------------------
# 7. USER INPUTS (left column) - 8 widgets of 6 different types
# -----------------------------------------------------------------------------
with left_column:
  with st.container(border=True, key="card_furniture"):
    st.subheader("1. Choose your furniture")
    # Widget 1: pills (click-to-select buttons) - furniture category
    category = st.pills(
      "Furniture category", list(FURNITURE_PRICES.keys()),
      format_func=category_label, key="category",
    )
    st.markdown("**Choose your preferred design**")
    design_options = PRODUCT_DESIGNS[category]
    design_columns = st.columns(3, gap="small")
    for design_col, (design_name, design_desc, design_image) in zip(design_columns, design_options):
      with design_col:
        st.image(design_image, use_container_width=True)
        st.markdown(f"**{design_name}**")
        st.caption(design_desc)
    design = st.radio(
      "Select a design",
      [item[0] for item in design_options],
      key="design_" + category,
      horizontal=False,
      label_visibility="collapsed",
    )
    # Widget 2: pills - material
    material = st.pills(
      "Material", ["Engineered Wood", "Solid Wood", "Metal"], key="material"
    )
    # Widget 3: radio buttons - size
    size = st.radio(
      "Size", ["Small", "Medium", "Large"], horizontal=True, key="size"
    )
    # Widget 4: number_input - quantity (min/max stop invalid values)
    quantity = st.number_input(
      "Quantity (number of items)",
      min_value=MIN_QUANTITY,
      max_value=MAX_QUANTITY,
      step=1,
      key="quantity",
    )

  with st.container(border=True, key="card_extras"):
    st.subheader("2. Extras and delivery")
    # Widget 5: checkbox - returns True or False
    wants_customization = st.checkbox(
      f"Add customization (+{format_rupees(CUSTOMIZATION_CHARGE_PER_ITEM)} per item)",
      key="customization",
    )
    # Widget 6: selectbox - delivery type
    delivery = st.selectbox(
      "Delivery type", ["Standard", "Express"], key="delivery"
    )
    st.caption(
      f"Standard: {format_rupees(STANDARD_DELIVERY_CHARGE)}, "
      f"{DELIVERY_DAYS['Standard']}  |  "
      f"Express: {format_rupees(EXPRESS_DELIVERY_CHARGE)}, "
      f"{DELIVERY_DAYS['Express']}"
    )

  with st.container(border=True, key="card_customer"):
    st.subheader("3. You and your budget")
    # Widget 7: radio buttons - customer type
    customer_type = st.radio(
      "Customer type", ["Regular", "Premium"], horizontal=True, key="customer_type"
    )
    st.caption(f"Premium customers get an extra {PREMIUM_EXTRA_DISCOUNT}% discount.")
    # Widget 8: slider - the customer's budget
    budget = st.slider(
      "Your budget (₹)", min_value=10000, max_value=500000, step=5000, key="budget"
    )

# -----------------------------------------------------------------------------
# 8. CALCULATION WITH ERROR HANDLING
# -----------------------------------------------------------------------------
try:
  bill = calculate_bill(
    category, material, size, quantity,
    wants_customization, delivery, customer_type,
  )
except ValueError as error:
  # Friendly message for invalid input - the app does not crash
  with right_column:
    st.error(f"️ {error}")
  st.stop()
except Exception:
  # Safety net for any unexpected problem
  with right_column:
    st.error("️ Something went wrong. Please check your inputs and try again.")
  st.stop()

# The list of (label, amount) pairs used for the table and the downloadable quote
breakdown_rows = [
  (f"Base price ({format_rupees(bill['base_price'])} × {bill['quantity']})",
   bill["base_price"] * bill["quantity"]),
  (f"Material adjustment ({material})",
   bill["material_adjustment"] * bill["quantity"]),
  (f"Size adjustment ({size})",
   bill["size_adjustment"] * bill["quantity"]),
  ("Furniture total", bill["furniture_total"]),
  ("Customization charges", bill["customization_charges"]),
  (f"Delivery charges ({delivery})", bill["delivery_charges"]),
  ("Subtotal", bill["subtotal"]),
  (f"Discount ({bill['discount_percent']}% on furniture + customization)",
   -bill["discount_amount"]),
]

# -----------------------------------------------------------------------------
# 9. RESULTS (right column) - live preview, then 3 tabs
# -----------------------------------------------------------------------------
with right_column:
  # ---- Live preview card: reacts to every choice ----
  chips_html = (
    f'<span class="chip chip-beige"><span class="swatch" '
    f'style="background:{MATERIAL_COLORS.get(material, "#D9B98A")}"></span>{material}</span>'
    f'<span class="chip chip-yellow">{size} size</span>'
    f'<span class="chip chip-blue"> {delivery}: {DELIVERY_DAYS[delivery]}</span>'
  )
  if wants_customization:
    chips_html = chips_html + '<span class="chip chip-yellow"> Customized</span>'
  if customer_type == "Premium":
    chips_html = chips_html + '<span class="chip chip-blue">⭐ Premium</span>'

  st.markdown(
    f'<div class="preview-card">'
    f'<div class="preview-icon">{CATEGORY_ICONS.get(category, "")}</div>'
    f'<div><div class="preview-title">{bill["quantity"]} × {category}</div>'
    f'<div><b>Design:</b> {design}</div><div>{chips_html}</div></div></div>',
    unsafe_allow_html=True,
  )

  with st.container(border=True, key="card_results"):
    tab_summary, tab_breakdown, tab_prices = st.tabs(
      [" Your bill", " Cost breakdown", " Price list"]
    )

    # ---------------- TAB 1: the final bill, discount meter, budget ----------------
    with tab_summary:
      st.markdown(
        f'<div class="bill-box">'
        f'<div class="bill-label">ESTIMATED FINAL BILL</div>'
        f'<div class="bill-amount">{format_rupees(bill["final_bill"])}</div>'
        f'<div class="bill-note">Subtotal {format_rupees(bill["subtotal"])} '
        f'− Discount {format_rupees(bill["discount_amount"])}</div></div>',
        unsafe_allow_html=True,
      )

      # Discount message
      if bill["discount_percent"] > 0:
        st.success(f" You saved {format_rupees(bill['discount_amount'])} "
              f"({bill['discount_percent']}% discount applied).")
      else:
        st.info("No discount yet. Order goods worth ₹40,000 or more to unlock one.")

      # Discount meter: how close is the customer to the next slab?
      goal_amount, goal_percent = get_next_discount_goal(bill["goods_total"])
      if goal_amount is None:
        st.markdown(" **Highest order-value discount unlocked!**")
        st.progress(1.0)
      else:
        still_needed = goal_amount - bill["goods_total"]
        st.markdown(
          f" **Add {format_rupees(still_needed)} more** of furniture "
          f"to unlock a **{goal_percent}%** order discount."
        )
        st.progress(min(bill["goods_total"] / goal_amount, 1.0))

      # Budget check
      st.markdown(f" **Your budget: {format_rupees(budget)}**")
      if bill["final_bill"] <= budget:
        money_left = budget - bill["final_bill"]
        st.success(f" Within budget! You still have {format_rupees(money_left)} left.")
      else:
        money_over = bill["final_bill"] - budget
        st.warning(f"️ Over budget by {format_rupees(money_over)}. "
              "Try a smaller size, Engineered Wood, or Standard delivery.")
      st.progress(min(bill["final_bill"] / budget, 1.0))

      # Build the text of the downloadable quote using a list and a loop
      quote_lines = [
        "HERITAGE OAK FURNITURE STUDIO - ESTIMATE",
        "-" * 44,
        f"Order: {bill['quantity']} x {category} - {design} ({material}, {size})",
        f"Customer type: {customer_type}",
        "-" * 44,
      ]
      for label, amount in breakdown_rows:
        quote_lines.append(f"{label}: {format_rupees(amount)}")
      quote_lines.append("-" * 44)
      quote_lines.append(f"FINAL BILL: {format_rupees(bill['final_bill'])}")
      quote_lines.append("This is an estimate. Prices include GST.")
      quote_text = "\n".join(quote_lines)

      button_left, button_right = st.columns(2)
      with button_left:
        # A button returns True only on the run when it is clicked
        if st.button(" Confirm my estimate", key="confirm_button"):
          st.balloons()
          st.toast("Estimate confirmed! Show it at our store.")
      with button_right:
        st.download_button(
          " Download my quote",
          data=quote_text,
          file_name="heritage_oak_quote.txt",
          mime="text/plain",
        )

    # ---------------- TAB 2: itemized table and cost share bars ----------------
    with tab_breakdown:
      st.markdown("**Itemized cost breakdown**")
      # Build a markdown table row by row using a for loop
      table_text = "| Cost item | Amount |\n|---|---:|\n"
      for label, amount in breakdown_rows:
        table_text = table_text + f"| {label} | {format_rupees(amount)} |\n"
      st.markdown(table_text)

      st.markdown("**Where your money goes (before discount)**")
      # (label, amount, colour class) for each bar
      cost_parts = [
        ("Furniture", bill["furniture_total"], "fill-brown"),
        ("Customization", bill["customization_charges"], "fill-yellow"),
        ("Delivery", bill["delivery_charges"], "fill-blue"),
      ]
      bars_html = ""
      for label, amount, color_class in cost_parts:
        percent = round(amount * 100 / bill["subtotal"])  # share of the subtotal
        bars_html = bars_html + (
          f'<div class="bar-row"><div class="bar-label">{label} ({percent}%)</div>'
          f'<div class="bar-track"><div class="bar-fill {color_class}" '
          f'style="width:{percent}%"></div></div>'
          f'<div class="bar-value">{format_rupees(amount)}</div></div>'
        )
      st.markdown(bars_html, unsafe_allow_html=True)

    # ---------------- TAB 3: price list and pricing rules ----------------
    with tab_prices:
      st.markdown("**Base price per item**")
      price_text = "| Category | Base price |\n|---|---:|\n"
      for name, price in FURNITURE_PRICES.items():
        price_text = price_text + f"| {CATEGORY_ICONS[name]} {name} | {format_rupees(price)} |\n"
      st.markdown(price_text)

      st.markdown(
        f"""
**Adjustments (percentage of base price)**
- Material: Engineered Wood +0%, Solid Wood +30%, Metal +10%
- Size: Small −10%, Medium +0%, Large +25%

**Charges**
- Customization: {format_rupees(CUSTOMIZATION_CHARGE_PER_ITEM)} per item
- Delivery (per order): Standard {format_rupees(STANDARD_DELIVERY_CHARGE)}, Express {format_rupees(EXPRESS_DELIVERY_CHARGE)}

**Discount rule** (on furniture + customization; delivery is not discounted)
- Goods value ₹40,000 or more: 5% | ₹75,000 or more: 7% | ₹1,50,000 or more: 10%
- Premium customers get an extra 5%

**Formulas**
- Subtotal = (Base + Material + Size) × Quantity + Customization + Delivery
- Final Bill = Subtotal − Discount (never below ₹0)

All prices are estimates in Indian rupees and are assumed to include GST.
        """
      )

st.write("")
st.caption("Heritage Oak Furniture Studio | Built with Python and Streamlit")

# ----------------------------------------------------------------------------
# 10. INFORMATION SECTIONS (placed below the furniture estimate)
# ----------------------------------------------------------------------------
st.divider()
st.markdown("## How it works")
steps = [
  ("01", "Choose your piece", "Select a furniture category and one of its three designs."),
  ("02", "Make it yours", "Choose material, size and quantity, then add customization if needed."),
  ("03", "Select delivery", "Choose standard or express delivery for your order."),
  ("04", "See your estimate", "Review the itemized calculation, applicable savings and final estimate."),
]
step_cols = st.columns(4, gap="medium")
for col, (number, title, description) in zip(step_cols, steps):
  with col:
    st.markdown(
      f'<div class="step-card"><div class="step-number">{number}</div>'
      f'<div class="step-title">{title}</div><div>{description}</div></div>',
      unsafe_allow_html=True,
    )

st.write("")
st.markdown("## Visit Us")
st.markdown(
  '<div class="review-card"><b>Heritage Oak Furniture Studio</b>'
  '<p><b>Showroom address:</b> O.P. Jindal Global University, Sonipat, Haryana, India</p>'
  '<p>For enquiries, please use the store contact details provided by the salesman.</p></div>',
  unsafe_allow_html=True,
)
