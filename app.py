import os
from dotenv import load_dotenv
import streamlit as st
from agent import analyze_ticket
from database import init_db, save_ticket, list_tickets

load_dotenv()
st.set_page_config(page_title='AI Support Ticket Assistant', page_icon='🛠️', layout='wide')
init_db()
st.title('🛠️ AI Support Ticket Assistant')
st.caption('Python + Gemini API + SQLite + Streamlit | Portfolio MVP')

with st.form('ticket_form'):
    description = st.text_area('Describe an IT problem', placeholder='My laptop cannot connect to Wi-Fi after a Windows update...', height=140)
    submitted = st.form_submit_button('Analyze & save')

if submitted:
    if not description.strip():
        st.warning('Please enter a ticket description.')
    elif len(description) > 3000:
        st.warning('Description is too long (max 3000 characters).')
    elif not os.getenv('GEMINI_API_KEY'):
        st.error('Set GEMINI_API_KEY in your .env file before running the app.')
    else:
        try:
            with st.spinner('Analyzing ticket...'):
                result = analyze_ticket(description)
            ticket_id = save_ticket(description, result['category'], result['priority'], result['solution'])
            st.success(f'Ticket #{ticket_id} saved')
            c1, c2 = st.columns(2)
            c1.metric('Category', result['category'])
            c2.metric('Priority', result['priority'])
            st.subheader('Suggested next steps')
            st.write(result['solution'])
            if result['tool_called']:
                st.success('AI agent used the search_tickets tool.')
            else:
                st.warning('The model did not use the search tool in this run.')
            if result['matched_tickets']:
                st.subheader('Similar previous tickets')
                st.dataframe(result['matched_tickets'], use_container_width=True, hide_index=True)
            else:
                st.caption('No matching historical tickets returned by the agent.')
            st.info('AI-generated suggestions must be checked by a human before implementation.')
        except Exception as exc:
            st.error(f'Could not analyze ticket: {exc}')

st.divider()

st.subheader("Ticket history")

rows = list_tickets()

if rows:
    st.dataframe(
        [
            {
                "ID": ticket["id"],
                "Category": ticket["category"],
                "Priority": ticket["priority"],
                "Date": ticket["created_at"]
            }
            for ticket in rows
        ],
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Ticket details")

    selected_id = st.selectbox(
        "Select a ticket",
        options=[ticket["id"] for ticket in rows],
        format_func=lambda ticket_id: f"Ticket #{ticket_id}"
    )

    selected_ticket = next(
        ticket for ticket in rows
        if ticket["id"] == selected_id
    )

    st.markdown("**Description**")
    st.write(selected_ticket["description"])

    st.markdown("**Suggested solution**")
    st.write(selected_ticket["solution"])

else:
    st.caption("No tickets yet.")

