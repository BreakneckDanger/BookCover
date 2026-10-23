import streamlit as st
from PIL import Image, ImageDraw
import io
import math

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="KDP Coloring Book Cover Studio",
    page_icon="🎨",
    layout="wide"
)

# --- CONSTANTS (From Specifications) ---
BASE_WIDTH = 8.5
BASE_HEIGHT = 11.0
SPINE_FACTOR = 0.002252
FULL_BLEED = 0.25
OUTER_BLEED = 0.125
DPI = 400
MIN_PAGES = 24
MAX_PAGES = 590

st.title("🎨 Amazon KDP Coloring Book Cover Studio")
st.markdown("**Standardized for 8.5\" x 11\" White Paper Paperbacks at 400 DPI**")

# --- SIDEBAR INPUTS ---
st.sidebar.header("📐 Book Parameters")
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
        f"ℹ️ Odd page count ({raw_page_count}) automatically rounded up to **{calc_page_count}** for spine calculation."
    )
else:
    calc_page_count = raw_page_count
    st.sidebar.success(f"✅ Using even page count: **{calc_page_count}**")

# --- CORE CALCULATIONS ---
spine_width_in = calc_page_count * SPINE_FACTOR
half_spine_in = spine_width_in / 2.0

# 1. Full Wrap Cover Formulas
full_width_in = (2 * BASE_WIDTH) + spine_width_in + FULL_BLEED
full_height_in = BASE_HEIGHT + FULL_BLEED

full_width_px = round(full_width_in * DPI)
full_height_px = round(full_height_in * DPI)
spine_width_px = round(spine_width_in * DPI)

# 2. Front Cover Canvas Formulas
front_width_in = BASE_WIDTH + OUTER_BLEED + half_spine_in
front_height_in = BASE_HEIGHT + FULL_BLEED

front_width_px = round(front_width_in * DPI)
front_height_px = round(front_height_in * DPI)

# --- DISPLAY METRICS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📘 Full Wrap Cover (Back + Spine + Front)")
    st.info("Use these dimensions for your final KDP upload canvas.")
    m1, m2, m3 = st.columns(3)
    m1.metric("Full Width", f"{full_width_in:.4f}\"", f"{full_width_px} px")
    m2.metric("Full Height", f"{full_height_in:.2f}\"", f"{full_height_px} px")
    m3.metric("Spine Width", f"{spine_width_in:.4f}\"", f"{spine_width_px} px")

    with st.expander("See Formula Breakdown"):
        st.write(f"- **Base Trim:** {BASE_WIDTH}\" x {BASE_HEIGHT}\"")
        st.write(f"- **Calculated Pages:** {calc_page_count}")
        st.write(f"- **Spine Width:** {calc_page_count} × {SPINE_FACTOR} = `{spine_width_in:.6f}\"`")
        st.write(f"- **Full Width:** (2 × {BASE_WIDTH}) + {spine_width_in:.6f} + {FULL_BLEED} = `{full_width_in:.6f}\"`")
        st.write(f"- **Full Height:** {BASE_HEIGHT} + {FULL_BLEED} = `{full_height_in:.2f}\"`")
        st.write(f"- **Pixel Dimensions (@ {DPI} DPI):** `{full_width_px} x {full_height_px} px`")

with col2:
    st.subheader("📗 Front Cover Canvas (Single Panel + Half Spine + Bleed)")
    st.info("Use these dimensions when designing the front cover panel separately.")
    f1, f2, f3 = st.columns(3)
    f1.metric("Front Width", f"{front_width_in:.4f}\"", f"{front_width_px} px")
    f2.metric("Front Height", f"{front_height_in:.2f}\"", f"{front_height_px} px")
    f3.metric("Half Spine Included", f"{half_spine_in:.4f}\"", f"{round(half_spine_in * DPI)} px")

    with st.expander("See Formula Breakdown"):
        st.write(f"- **Half Spine Width:** ({calc_page_count} × {SPINE_FACTOR}) / 2 = `{half_spine_in:.6f}\"`")
        st.write(f"- **Front Width:** {BASE_WIDTH} (Base) + {OUTER_BLEED} (Outer Bleed) + {half_spine_in:.6f} (Half Spine) = `{front_width_in:.6f}\"`")
        st.write(f"- **Front Height:** {BASE_HEIGHT} (Base) + {FULL_BLEED} (Height Bleed) = `{front_height_in:.2f}\"`")
        st.write(f"- **Pixel Dimensions (@ {DPI} DPI):** `{front_width_px} x {front_height_px} px`")

st.divider()

# --- TEMPLATE & COVER BUILDER ---
st.subheader("🛠️ Cover Template & Builder (@ 400 DPI)")
tab1, tab2 = st.tabs(["📥 Download Blank Guide Templates", "🖼️ Combine Front & Back Artwork"])

def generate_template(is_full_wrap=True):
    """Generates a 400 DPI PNG guide template showing bleed and spine lines."""
    w = full_width_px if is_full_wrap else front_width_px
    h = full_height_px if is_full_wrap else front_height_px
    
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)
    bleed_px = round(OUTER_BLEED * DPI) # 50 px at 400 DPI
    
    # Draw Outer Bleed Boundary (Red)
    draw.rectangle([bleed_px, bleed_px, w - bleed_px, h - bleed_px], outline="#FF4B4B", width=6)
    
    if is_full_wrap:
        # Spine boundaries (Blue)
        left_spine_x = round((OUTER_BLEED + BASE_WIDTH) * DPI)
        right_spine_x = left_spine_x + spine_width_px
        draw.line([(left_spine_x, 0), (left_spine_x, h)], fill="#1C83E1", width=6)
        draw.line([(right_spine_x, 0), (right_spine_x, h)], fill="#1C83E1", width=6)
    else:
        # Half-spine fold line on the left side of the front cover (Blue)
        half_spine_px = round(half_spine_in * DPI)
        draw.line([(half_spine_px, 0), (half_spine_px, h)], fill="#1C83E1", width=6)
        
    return img

with tab1:
    st.write("Download exact **400 DPI PNG templates** to import into Procreate, Canva, or Photoshop. Red lines indicate the 0.125\" trim/bleed line; blue lines indicate spine fold lines.")
    t_col1, t_col2 = st.columns(2)
    
    with t_col1:
        if st.button("Generate Full Wrap Guide (400 DPI)"):
            with st.spinner("Creating high-res template..."):
                full_tpl = generate_template(is_full_wrap=True)
                st.image(full_tpl, caption=f"Full Wrap Preview ({full_width_px}x{full_height_px} px)", use_container_width=True)
                buf = io.BytesIO()
                full_tpl.save(buf, format="PNG", dpi=(DPI, DPI))
                st.download_button(
                    label="⬇️ Download Full Wrap Template (PNG)",
                    data=buf.getvalue(),
                    file_name=f"KDP_Full_Wrap_{calc_page_count}pgs_{full_width_px}x{full_height_px}px_400DPI.png",
                    mime="image/png"
                )

    with t_col2:
        if st.button("Generate Front Cover Guide (400 DPI)"):
            with st.spinner("Creating high-res template..."):
                front_tpl = generate_template(is_full_wrap=False)
                st.image(front_tpl, caption=f"Front Cover Preview ({front_width_px}x{front_height_px} px)", use_container_width=True)
                buf = io.BytesIO()
                front_tpl.save(buf, format="PNG", dpi=(DPI, DPI))
                st.download_button(
                    label="⬇️ Download Front Cover Template (PNG)",
                    data=buf.getvalue(),
                    file_name=f"KDP_Front_Cover_{calc_page_count}pgs_{front_width_px}x{front_height_px}px_400DPI.png",
                    mime="image/png"
                )

with tab2:
    st.write("Upload your Front Cover and Back Cover designs to automatically stitch them into a **Full Wrap 400 DPI Cover** (PNG & PDF).")
    u_col1, u_col2, u_col3 = st.columns(3)
    front_file = u_col1.file_uploader("Upload Front Cover Image", type=["png", "jpg", "jpeg"])
    back_file = u_col2.file_uploader("Upload Back Cover Image (Optional)", type=["png", "jpg", "jpeg"])
    bg_color = u_col3.color_picker("Base / Spine Color", "#FFFFFF")

    if front_file:
        with st.spinner("Processing 400 DPI Full Wrap Cover..."):
            canvas = Image.new("RGB", (full_width_px, full_height_px), bg_color)
            
            # Place Back Cover (if uploaded) on left half
            if back_file:
                back_img = Image.open(back_file).convert("RGB")
                back_img = back_img.resize((front_width_px, front_height_px), Image.Resampling.LANCZOS)
                canvas.paste(back_img, (0, 0))
                
            # Place Front Cover on right half
            front_img = Image.open(front_file).convert("RGB")
            front_img = front_img.resize((front_width_px, front_height_px), Image.Resampling.LANCZOS)
            canvas.paste(front_img, (full_width_px - front_width_px, 0))
            
            st.image(canvas, caption="Assembled Full Wrap Cover", use_container_width=True)
            
            # Export buttons
            dl_col1, dl_col2 = st.columns(2)
            
            png_buf = io.BytesIO()
            canvas.save(png_buf, format="PNG", dpi=(DPI, DPI))
            dl_col1.download_button(
                "⬇️ Download Full Wrap PNG (400 DPI)",
                data=png_buf.getvalue(),
                file_name=f"Final_Full_Cover_{calc_page_count}pgs_400DPI.png",
                mime="image/png"
            )
            
            pdf_buf = io.BytesIO()
            canvas.save(pdf_buf, format="PDF", resolution= float(DPI))
            dl_col2.download_button(
                "⬇️ Download Print-Ready PDF (400 DPI)",
                data=pdf_buf.getvalue(),
                file_name=f"Final_Full_Cover_{calc_page_count}pgs_400DPI.pdf",
                mime="application/pdf"
            )
          
