import streamlit as st
import pandas as pd
from deep_translator import GoogleTranslator
import io

st.set_page_config(
    page_title="Excel Column Translator",
    page_icon="🌍",
    layout="centered"
)

@st.cache_data(show_spinner=False)
def translate_text(text):
    """
    Translates text to English with automatic language detection.
    Handles empty cells and potential API errors gracefully.
    """
    # Skip empty, NaN, or whitespace-only cells
    if pd.isna(text) or str(text).strip() == "":
        return text
    
    try:
        # source='auto' automatically detects the original language
        translator = GoogleTranslator(source='auto', target='en')
        return translator.translate(str(text))
    except Exception as e:
        # If an error occurs (e.g., network issue), return original with error note
        return f"[Error: {e}] {text}"

st.title("🌍 Excel Column Auto-Translator")
st.markdown("Upload an Excel file, select a column containing text in any language, and automatically translate it to English. The output will maintain your original file structure.")

# File uploader restricted to Excel files
uploaded_file = st.file_uploader("Upload your Excel file (.xlsx or .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Read the excel file into a pandas dataframe
        df = pd.read_excel(uploaded_file)
        
        st.success("File uploaded successfully!")
        st.write("### Data Preview (First 5 Rows)")
        st.dataframe(df.head())

        st.write("### Translation Settings")
        
        # Get list of columns
        columns = df.columns.tolist()
        
        # User selects the column they want to translate
        selected_column = st.selectbox(
            "Select the column you want to translate to English:",
            options=columns
        )

        # Optional: Ask user if they want to overwrite the column or create a new one
        output_preference = st.radio(
            "Translation Output Preference:",
            ("Overwrite existing column", "Create a new column (Append '_English')")
        )

        if st.button("Translate Column"):
            # Create a copy of the dataframe to manipulate
            translated_df = df.copy()
            
            # Setup a progress bar to keep the user informed
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_rows = len(translated_df)
            translated_values = []
            
            # Iterate through the rows of the selected column and translate
            for index, value in enumerate(translated_df[selected_column]):
                # Update status
                status_text.text(f"Translating row {index + 1} of {total_rows}...")
                
                # Perform translation
                translated_val = translate_text(value)
                translated_values.append(translated_val)
                
                # Update progress bar
                progress = (index + 1) / total_rows
                progress_bar.progress(progress)
            
            # Apply the translated list back to the dataframe based on user preference
            if output_preference == "Overwrite existing column":
                translated_df[selected_column] = translated_values
            else:
                new_col_name = f"{selected_column}_English"
                # Insert right next to original column
                col_idx = translated_df.columns.get_loc(selected_column) + 1
                translated_df.insert(col_idx, new_col_name, translated_values)

            status_text.text("Translation complete!")
            st.write("### Translated Data Preview")
            st.dataframe(translated_df.head())

            # Save the new dataframe to a BytesIO buffer so the user can download it
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                translated_df.to_excel(writer, index=False, sheet_name='Translated_Data')
            
            # Prepare download button
            st.download_button(
                label="📥 Download Translated Excel File",
                data=buffer.getvalue(),
                file_name="translated_file.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")