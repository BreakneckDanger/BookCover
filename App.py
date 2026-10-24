import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="KDP Coloring Book Cover Studio",
    page_icon="🎨",
    layout="wide"
)

# --- CONSTANTS (From KDP Specifications) ---
BASE_WIDTH = 8.5
BASE_HEIGHT = 11.0
SPINE_FACTOR = 0.002252
FULL_BLEED = 0.25
OUTER_BLEED = 0.125
DPI = 400
MIN_PAGES = 24
MAX_PAGES = 590

st.title("🎨 Amazon KDP Coloring Book Cover Studio")
st.markdown("**8.5\" x 11\" White Paper Paperback • Standardized at 400 DPI**")

# --- SIDEBAR: PAGE COUNT & DIMENSIONS ---
st.sidebar.header("📐 1. Book Page Count")
raw_page_count = st.sidebar.number_input(
    "Enter Page Count (24 - 590):",
    min_value=MIN_PAGES,
    max_value=MAX_PAGES,
    value=50,
    step=1
)

# Page Rounding Rule: If odd, round up to next even number
if raw_page_count % 2 != 0:
    calc_page_count = raw_page_count + 1
    st.sidebar.warning(
        f"ℹ️ Odd page count ({raw_page_count}) rounded up to **{calc_page_count}** for spine calculation."
    )
else:
    calc_page_count = raw_page_count
    st.sidebar.success(f"✅ Using even page count: **{calc_page_count}**")

# --- CORE FORMULA CALCULATIONS ---
spine_width_in = calc_page_count * SPINE_FACTOR
half_spine_in = spine_width_in / 2.0

# Full Wrap Cover
full_width_in = (2 * BASE_WIDTH) + spine_width_in + FULL_BLEED
full_height_in = BASE_HEIGHT + FULL_BLEED
full_width_px = round(full_width_in * DPI)
full_height_px = round(full_height_in * DPI)
spine_width_px = round(spine_width_in * DPI)

# Front Cover Canvas (Single Panel + Half Spine + Outer Bleed)
front_width_in = BASE_WIDTH + OUTER_BLEED + half_spine_in
front_height_in = BASE_HEIGHT + FULL_BLEED
front_width_px = round(front_width_in * DPI)
front_height_px = round(front_height_in * DPI)

# Key Pixel Coordinates on Full Wrap Canvas
bleed_px = round(OUTER_BLEED * DPI)  # 50 px
back_trim_px = round(BASE_WIDTH * DPI)  # 3400 px
left_spine_x = bleed_px + back_trim_px  # 3450 px
right_spine_x = left_spine_x + spine_width_px

# --- COMPACT DIMENSIONS SUMMARY ---
with st.expander("📊 View Exact KDP Dimensions & Formula Math (Inches & 400 DPI Pixels)", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📘 Full Wrap Cover (Back + Spine + Front)")
        st.write(f"- **Full Width:** `{full_width_in:.4f}\"` (**{full_width_px} px**)")
        st.write(f"- **Full Height:** `{full_height_in:.2f}\"` (**{full_height_px} px**)")
        st.write(f"- **Spine Width:** `{spine_width_in:.4f}\"` (**{spine_width_px} px**)")
    with col2:
        st.markdown("#### 📗 Front Cover Panel (Base + Outer Bleed + Half Spine)")
        st.write(f"- **Front Width:** `{front_width_in:.4f}\"` (**{front_width_px} px**)")
        st.write(f"- **Front Height:** `{front_height_in:.2f}\"` (**{front_height_px} px**)")
        st.write(f"- **Half Spine:** `{half_spine_in:.4f}\"` (**{round(half_spine_in * DPI)} px**)")

# --- HELPER: LOAD FONT ---
def get_font(size):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except Exception:
        return ImageFont.load_default(size=size)

# --- TABS ---
tab_auto, tab_stitch, tab_guides = st.tabs([
    "✨ 1. Auto-Cover Studio (Skip Canva!)",
    "🖼️ 2. Stitch Pre-Made Front & Back",
    "📥 3. Download Blank Guide Templates"
])

# ==============================================================================
# TAB 1: AUTO-COVER STUDIO (RAW ART -> FINISHED KDP COVER)
# ==============================================================================
with tab_auto:
    st.subheader("✨ Automatic Raw Artwork to KDP Full-Wrap Cover")
    st.write("Upload your raw illustration, customize your colors, text, and back-cover sample pages, and export a 400 DPI print-ready PDF directly!")

    ctrl_col, prev_col = st.columns([1, 1.4])

    with ctrl_col:
        st.markdown("##### 🖼️ Step 1: Upload Raw Front Artwork")
        raw_front = st.file_uploader("Upload Front Illustration (Square, Portrait, etc.)", type=["png", "jpg", "jpeg"])
        
        art_placement = st.radio(
            "Where should the front art start?",
            ["Start at Spine Edge (Clean Spine)", "Include Half-Spine (Front Canvas Formula)"],
            help="'Start at Spine Edge' keeps your spine a solid color. 'Include Half-Spine' extends your art halfway across the spine."
        )
        fit_mode = st.selectbox(
            "Artwork Scaling Mode:",
            [
                "Smart Fill / Center Crop (Fills entire front cover + bleed)",
                "Fit Inside with Border (No cropping, adds margin around art)"
            ]
        )
        if "Border" in fit_mode:
            border_in = st.slider("Front Border Thickness (inches):", 0.0, 1.5, 0.5, 0.1)
        else:
            border_in = 0.0

        st.markdown("##### 🎨 Step 2: Background, Spine & Back Cover")
        c1, c2 = st.columns(2)
        bg_color = c1.color_picker("Back & Spine Color", "#2B2D42")
        accent_color = c2.color_picker("Frame / Banner Color", "#FFFFFF")

        back_samples = st.file_uploader(
            "Upload 1–3 Inside Coloring Pages (Auto-creates Back Cover Previews!)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True
        )
        back_blurb = st.text_area("Back Cover Tagline / Blurb (Optional):", value="Hours of relaxing creativity and fun!", height=68)

        st.markdown("##### 🔤 Step 3: Optional Cover Text Overlay")
        add_text = st.checkbox("Add Title / Author Text on Front Cover", value=False)
        if add_text:
            book_title = st.text_input("Main Book Title:", "MANDALA DREAMS")
            book_subtitle = st.text_input("Subtitle:", "A Stress-Relief Coloring Book")
            author_name = st.text_input("Author / Brand Name:", "By Sister Studio Press")
            t_col1, t_col2 = st.columns(2)
            text_color = t_col1.color_picker("Text Color", "#2B2D42")
            banner_bg = t_col2.checkbox("Show Solid Banner Behind Title", value=True)
            title_y_pct = st.slider("Title Vertical Position (% from top):", 8, 85, 18)

        st.markdown("##### 🔍 Step 4: Preview Guides")
        show_guides = st.checkbox(
            "Show KDP Bleed, Spine & Barcode Safe-Zone Guides on Preview",
            value=True,
            help="Guides are ONLY shown in the preview so you can check alignment. Your download buttons below will ALWAYS be clean without lines!"
        )

    with prev_col:
        # Create full 400 DPI canvas
        canvas = Image.new("RGB", (full_width_px, full_height_px), bg_color)
        draw = ImageDraw.Draw(canvas)

        # Determine target Front Cover X region
        if "Start at Spine Edge" in art_placement:
            front_start_x = right_spine_x
        else:
            front_start_x = full_width_px - front_width_px
        target_front_w = full_width_px - front_start_x
        target_front_h = full_height_px

        # 1. Place Raw Front Artwork
        if raw_front:
            art_img = Image.open(raw_front).convert("RGB")
            if "Smart Fill" in fit_mode:
                fitted_art = ImageOps.fit(art_img, (target_front_w, target_front_h), method=Image.Resampling.LANCZOS)
                canvas.paste(fitted_art, (front_start_x, 0))
            else:
                pad_px = round(border_in * DPI)
                inner_w = max(100, target_front_w - (2 * pad_px) - bleed_px)
                inner_h = max(100, target_front_h - (2 * pad_px) - (2 * bleed_px))
                art_img.thumbnail((inner_w, inner_h), Image.Resampling.LANCZOS)
                
                # Draw subtle frame behind fitted image
                paste_x = right_spine_x + ((full_width_px - bleed_px - right_spine_x - art_img.width) // 2)
                paste_y = bleed_px + ((full_height_px - (2 * bleed_px) - art_img.height) // 2)
                frame_pad = 16
                draw.rectangle(
                    [paste_x - frame_pad, paste_y - frame_pad, paste_x + art_img.width + frame_pad, paste_y + art_img.height + frame_pad],
                    fill=accent_color
                )
                canvas.paste(art_img, (paste_x, paste_y))

        # 2. Place Front Text Overlay (if enabled)
        if add_text:
            front_center_x = right_spine_x + ((full_width_px - bleed_px - right_spine_x) // 2)
            title_y = round((title_y_pct / 100.0) * full_height_px)
            
            font_title = get_font(190)
            font_sub = get_font(95)
            font_auth = get_font(85)

            if banner_bg:
                banner_h = 460 if book_subtitle else 310
                draw.rectangle(
                    [right_spine_x, title_y - 170, full_width_px, title_y - 170 + banner_h],
                    fill=accent_color
                )

            if book_title:
                draw.text((front_center_x, title_y), book_title, fill=text_color, font=font_title, anchor="mm")
            if book_subtitle:
                draw.text((front_center_x, title_y + 165), book_subtitle, fill=text_color, font=font_sub, anchor="mm")
            if author_name:
                auth_y = full_height_px - bleed_px - 240
                draw.text(
                    (front_center_x, auth_y),
                    author_name,
                    fill=accent_color if not banner_bg else text_color,
                    font=font_auth,
                    anchor="mm",
                    
