import os
import streamlit as st
import PyPDF2
import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go

# Set up Google Gemini API Key
GEMINI_API_KEY = " "
genai.configure(api_key=GEMINI_API_KEY)


# Streamlit UI
st.set_page_config(page_title="AI Personal Finance Assistant", page_icon="", layout="wide")

# Custom CSS for Styling
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 34px;
        font-weight: bold;
        color: #4CAF50;
        text-shadow: 2px 2px 5px rgba(76, 175, 80, 0.4);
    }
    .sub-title {
        text-align: center;
        font-size: 18px;
        color: #ddd;
        margin-bottom: 20px;
    }
    .stButton button {
        background: linear-gradient(to right, #4CAF50, #388E3C);
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton button:hover {
        background: linear-gradient(to right, #388E3C, #2E7D32);
    }
    .result-card {
        background: rgba(0, 150, 136, 0.1);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0px 2px 8px rgba(0, 150, 136, 0.2);
    }
    .success-banner {
        background: linear-gradient(to right, #2E7D32, #1B5E20);
        color: white;
        padding: 15px;
        font-size: 18px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin-top: 15px;
        box-shadow: 0px 2px 8px rgba(0, 150, 136, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar with usage info
st.sidebar.title("ℹ️ How to Use This Tool?")
st.sidebar.write("- Upload your Savings Transaction History PDF.")
st.sidebar.write("- The AI will analyze your transactions.")
st.sidebar.write("- You will receive financial insights including income, expenses, savings, and spending trends.")
st.sidebar.write("- Use this data to plan your finances effectively.")

st.markdown('<h1 class="main-title">💸 AI-Powered Personal Finance Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Upload your Savings Transaction History PDF for Financial Insights</p>', unsafe_allow_html=True)

# Upload PDF File
uploaded_file = st.file_uploader("📂 Upload PDF File", type=["pdf"], help="Only PDF files are supported")

def extract_text_from_pdf(file_path):
    """Extracts text from the uploaded PDF file."""
    text = ""
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def analyze_financial_data(text):
    """Sends extracted text to Google Gemini AI for financial insights and
       requests structured data for a DataFrame.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
   
    prompt = f"""
    Analyze the following Paytm transaction history and extract monthly debit and credit amounts.
    Provide the results in a markdown table with the following columns:
    'Month', 'Debit', 'Credit'.
    Ensure the 'Month' column is in a format like 'YYYY-MM'.
    Also, provide a separate section for general financial insights.

    Financial Statement Text:
    {text}

    Desired Output Structure:
    **Monthly Financial Summary Table:**
    | Month   | Debit    | Credit   |
    |---------|----------|----------|
    | YYYY-MM | [Amount] | [Amount] |
    | YYYY-MM | [Amount] | [Amount] |
    | ...     | ...      | ...      |
    **General Financial Insights:**
    Analyze the following Savings transaction history and generate financial insights:
    {text}
    Provide a detailed breakdown in the following format:
    **Financial Insights for [User Name]**
    **Key Details:**
    - **Overall Monthly Income & Expenses:**
      - Month: [Month]
      - Income: ₹[Amount]
      - Expenses: ₹[Amount]
    - **Unnecessary Expenses Analysis:**
      - Expense Category: [Category Name]
      - Amount: ₹[Amount]
      - Recommendation: [Suggestion]
    - **Savings Percentage Calculation:**
      - Savings Percentage: [Percentage] %
    - **Expense Trend Analysis:**
      - Notable Trends: [Trend Details]
    - **Cost Control Recommendations:**
      - Suggestion: [Detailed Suggestion]
    - **Category-Wise Spending Breakdown:**
      - Category: [Category Name] - ₹[Amount]
      **Total debit and credit details:**
      - Total Debits: ₹[Total Debits]
      - Total Credits: ₹[Total Credits]
    - **Overall Financial Health:**
      - Summary: [Summary of Financial Health]
      **Actionable Insights:**
      - [Actionable Insights]
      **Next Steps:**
      - [Next Steps for Financial Planning]
      **Additional Notes:**
      - [Any Additional Notes]
      **Important Considerations:**
      - [Important Considerations for Financial Planning]
      **Income and Expense Summary:**
      - **Total Income:** ₹[Total Income]
      - **Total Expenses:** ₹[Total Expenses]
      - **Net Savings:** ₹[Net Savings]
      **Note:** Ensure the analysis is comprehensive and actionable, providing clear insights for financial planning.
      **Format the response in Markdown for better readability.
      **Ensure the response is concise and focused on financial insights.
      **Use bullet points for clarity and easy understanding.
      **Avoid jargon and keep the language simple and user-friendly.
      **Ensure the response is tailored for a user with basic financial knowledge.
      **Ensure the response is structured and easy to follow.
      **Ensure the response is suitable for a personal finance report.
      **Ensure the response is actionable and provides clear next steps for the user.
      **Ensure the response is comprehensive and covers all aspects of the financial data provided.   
    """
    response = model.generate_content(prompt)
    return response.text.strip() if response else "⚠️ Error processing financial data."

if uploaded_file is not None:
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ File uploaded successfully!")

    with st.spinner("📄 Extracting text from document..."):
        extracted_text = extract_text_from_pdf(file_path)

    if not extracted_text:
        st.error("⚠️ Failed to extract text. Ensure the document is not a scanned image PDF.")
    else:
        progress_bar = st.progress(0)
        with st.spinner("🧠 AI is analyzing your financial data..."):
            insights = analyze_financial_data(extracted_text)

        progress_bar.progress(100)

        st.subheader("📊 Financial Insights Report")
        st.markdown(f'<div class="result-card"><b>📄 Financial Report for {uploaded_file.name}</b></div>', unsafe_allow_html=True)
        monthly_data_df = None
        insights_text = ""
        try:
            lines = insights.split('\n')
            table_lines = []
            in_table = False
            in_insights = False
            for line in lines:
                if line.strip() == "**Monthly Financial Summary Table:**":
                    in_table = True
                    in_insights = False
                    continue
                elif line.strip() == "**General Financial Insights:**":
                    in_table = False
                    in_insights = True
                    continue

                if in_table and line.strip().startswith('|'):
                     table_lines.append(line.strip())
                elif in_insights:
                    insights_text += line + "\n"

            if table_lines and len(table_lines) > 2: # Need header, separator, and at least one data row
                # Parse the markdown table
                header = [h.strip() for h in table_lines[0].strip('|').split('|')]
                data_rows = []
                # Skip the separator line
                for row_line in table_lines[2:]:
                    row_data = [d.strip() for d in row_line.strip('|').split('|')]
                    if len(row_data) == len(header):
                         # Attempt to convert relevant columns to numeric
                        processed_row = []
                        for i, val in enumerate(row_data):
                            if header[i].lower() in ['debit', 'credit']:
                                try:
                                    # Clean the string before converting to float
                                    cleaned_val = val.replace('₹', '').replace('$', '').replace(',', '').strip()
                                    processed_row.append(float(cleaned_val))
                                except ValueError:
                                    processed_row.append(val) # Keep as string if conversion fails
                            else:
                                processed_row.append(val)
                        data_rows.append(processed_row)

                if data_rows:
                    monthly_data_df = pd.DataFrame(data_rows, columns=header)
                    st.subheader("📊 Monthly Debit and Credit Data:")
                    st.dataframe(monthly_data_df)

                    # You can now use `monthly_data_df` for plotting or further analysis.
                    # For example, plotting month-wise debit and credit:
                    if 'Month' in monthly_data_df.columns and 'Debit' in monthly_data_df.columns and 'Credit' in monthly_data_df.columns:
                        # Ensure numeric types for plotting
                        monthly_data_df['Debit'] = pd.to_numeric(monthly_data_df['Debit'], errors='coerce').fillna(0)
                        monthly_data_df['Credit'] = pd.to_numeric(monthly_data_df['Credit'], errors='coerce').fillna(0)

                        st.subheader("📈 Monthly Debit vs. Credit Plot")
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=monthly_data_df['Month'], y=monthly_data_df['Debit'], name='Debit', marker_color='red'))
                        fig.add_trace(go.Bar(x=monthly_data_df['Month'], y=monthly_data_df['Credit'], name='Credit', marker_color='green'))
                        fig.update_layout(title="Monthly Debit vs. Credit", xaxis_title="Month", yaxis_title="Amount")
                        st.plotly_chart(fig)

            if insights_text:
                st.subheader("📝 General Financial Insights:")
                st.write(insights_text)
        except Exception as parse_error:
            st.warning(f"Could not automatically parse data table or insights from AI output: {parse_error}")
            st.write("Raw AI Output:")
            st.write(insights) # Display raw output if parsing fails

        st.markdown('<div class="success-banner">🎊 Analysis Completed! Plan your finances wisely. 🚀</div>', unsafe_allow_html=True)
        st.balloons()

    os.remove(file_path)  # Cleanup