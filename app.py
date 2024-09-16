import streamlit as st
from pydantic import BaseModel, Field
from datetime import date
import plotly.graph_objects as go

class Retirement(BaseModel):
    monthly_expense: float = Field(gt=0, description="Monthly expenses")
    dob: date = Field(le=date.today(), description="Date of birth")
    retire_age: int = Field(default=60, description="Retirement Age")
    inflation_rate: float = Field(ge=0.0, le=100.0, default=8.0 , description="Inflation rate in percent")
    withdrawal_rate: float = Field(ge=0.0, le=100.0, default=3.0 , description="Withdrawal rate in percent")
    expected_return: float = Field(ge=0.0, le=100.0, default=12.0 , description="Expected return in percent")

    def get_age(self):
        today = date.today()
        age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return age

    def get_years_to_retire(self):
        age = self.get_age()
        years_to_retire = self.retire_age - age
        if years_to_retire <= 0:
            raise ValueError("Years to retire cannot be negative")
        return years_to_retire

    def get_total_corpus(self):
        annual_expense = self.monthly_expense * 12
        years_to_retire = self.get_years_to_retire()
        future_value = annual_expense * (1 + self.inflation_rate / 100) ** years_to_retire
        return future_value / (self.withdrawal_rate / 100)

    def estimate_sip(self):
        i = self.expected_return / 1200
        n = self.get_years_to_retire() * 12
        m = self.get_total_corpus()
        x = (1 + i) ** n - 1
        y = (x / i) * (1 + i)
        return m / y

st.title("Retirement Planning App")

# User Inputs
monthly_expense = st.number_input("Monthly Expenses (INR)", min_value=0.0, value=50000.0)
dob = st.date_input("Date of Birth", value=date(1990, 1, 1))
retire_age = st.number_input("Retirement Age", min_value=30, max_value=100, value=60)
inflation_rate = st.number_input("Inflation Rate (%)", min_value=0.0, max_value=100.0, value=8.0)
withdrawal_rate = st.number_input("Withdrawal Rate (%)", min_value=0.0, max_value=100.0, value=3.0)
expected_return = st.number_input("Expected Return (%)", min_value=0.0, max_value=100.0, value=12.0)

# Create Retirement Object
retirement = Retirement(
    monthly_expense=monthly_expense,
    dob=dob,
    retire_age=retire_age,
    inflation_rate=inflation_rate,
    withdrawal_rate=withdrawal_rate,
    expected_return=expected_return
)

# Calculate Results
try:
    years_to_retire = retirement.get_years_to_retire()
    total_corpus = retirement.get_total_corpus()
    sip_amount = retirement.estimate_sip()
    total_investement = sip_amount*years_to_retire*12
    intrest = total_corpus - total_investement

    st.subheader("Results")
    st.write(f"Years to Retirement: {years_to_retire}")
    st.write(f"Total Corpus Needed: {total_corpus:,.2f} INR")
    st.write(f"Estimated SIP: {sip_amount:,.2f} INR")
    st.write(f"Invested amount: {total_investement:,.2f} INR")
    st.write(f"Total Intrest : {intrest:,.2f} INR")


    # Plotly Chart
    fig = go.Figure()

    # Adding Total Corpus
    fig.add_trace(go.Bar(
        x=["Total Corpus Needed"],
        y=[total_corpus],
        name="Total Corpus Needed",
        marker_color='indianred'
    ))

    # Adding Invested amount
    fig.add_trace(go.Bar(
        x=["Invested Amount"],
        y=[total_investement],
        name="Invested amount",
        marker_color='lightblue'
    ))

    fig.update_layout(
        title_text='Retirement Planning Results',
        xaxis_title='Category',
        yaxis_title='Amount (INR)',
        barmode='group'
    )

    st.plotly_chart(fig)

except ValueError as e:
    st.error(str(e))
