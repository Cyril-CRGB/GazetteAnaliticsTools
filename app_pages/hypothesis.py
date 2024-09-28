import streamlit as st

def hypothesis_body():

    st.write("## Hypothesis")
    st.info(
        f"**1** We expected that **Damage** and **Amount** would be done depending on the identity of the victim.\n"
        f"\n**2** We expected that **Damage** and **Amount** would be correlated to the **Weapon Used Cd** and **Crm Cd** (crime committed).\n"
        f"\n**3** We expected that **Damage** and **Amount** would be correlated to **Area** and **Time OCC**.\n"
    )

    st.write("## Validation")
    st.success(
        f"**1** The correlation study ***support*** this, we see that **Vict Sex**, **Vict Descent** and **Vict Age** are amongst the top 6 features.\n"
        f"\n**2** The correlation study ***support*** this, **Weapon Used Cd** is in both case the best correlated feature.\n"
        f"\n**3** The correlation study ***does not support*** this. We really expected crime to occurs at night, outside in the weekend and/or in area where a lot of damage could be caused (richer area).\n"
    )