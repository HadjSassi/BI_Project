import streamlit as st
from MySql import connect_to_mysql, close_connection
from Config import *
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Initialisation de st.session_state.user à None
if "user" not in st.session_state:
    st.session_state.user = None

def login():
    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        # Connexion à la base de données
        connection = connect_to_mysql(HOST, USER_NAME, PASSWORD, DATABASE)

        if connection:
            # Obtenez le curseur pour exécuter des requêtes SQL
            cursor = connection.cursor()

            # Vérification des informations d'identification de l'utilisateur dans la base de données
            cursor.execute("SELECT * FROM user WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()

            if user:
                st.session_state.user = user
                st.success("Connexion réussie!")
                # Actualisation de la page après la connexion réussie
                st.experimental_rerun()
            else:
                st.error("Email ou mot de passe incorrect")

            # Fermer la connexion lorsque vous avez terminé
            close_connection(connection)
        else:
            st.error("Impossible de se connecter à la base de données.")

def get_data_medical():
    # Connexion à la base de données
    connection = connect_to_mysql(HOST, USER_NAME, PASSWORD, DATABASE)

    if connection:
        # Obtenez le curseur pour exécuter des requêtes SQL
        cursor = connection.cursor()

        # Requête pour obtenir le nombre de décès par maladie
        cursor.execute("SELECT disease_id, SUM(death_cases) AS total_deaths FROM fact_covid_data WHERE Date_id BETWEEN '2020-01-01' AND '2024-01-01' GROUP BY disease_id")
        data_by_disease = cursor.fetchall()

        # Requête pour obtenir les données par maladie pour le graphique de ligne
        cursor.execute("SELECT dim_covid_date.date, dim_covid_disease.disease_type, SUM(fact_covid_data.death_cases) AS total_deaths FROM fact_covid_data JOIN dim_covid_date ON fact_covid_data.Date_id = dim_covid_date.date JOIN dim_covid_disease ON fact_covid_data.disease_id = dim_covid_disease.disease_type WHERE Date_id BETWEEN '2020-01-01' AND '2024-01-01' GROUP BY dim_covid_date.date, dim_covid_disease.disease_type ORDER BY dim_covid_date.date")
        data_for_line_chart = cursor.fetchall()

        # Fermer la connexion lorsque vous avez terminé
        close_connection(connection)

        return data_by_disease, data_for_line_chart
    else:
        st.error("Impossible de se connecter à la base de données.")

def display_medical_page():
    st.title("Page médicale")

    # Obtenir les données
    data_by_disease, data_for_line_chart = get_data_medical()

    # Convertir les résultats des requêtes en DataFrame
    df_by_disease = pd.DataFrame(data_by_disease, columns=['Maladie', 'Nombre de décès'])
    df_for_line_chart = pd.DataFrame(data_for_line_chart, columns=['Date', 'Maladie', 'Nombre de décès'])

    # Affichage du graphique en secteurs (pie chart) du nombre de décès par maladie
    fig_pie = px.pie(df_by_disease, values='Nombre de décès', names='Maladie', title='Nombre de décès par maladie')
    st.plotly_chart(fig_pie)

    # Affichage du graphique de ligne (timeline chart) pour chaque maladie
    fig_line = go.Figure()

    for disease, data in df_for_line_chart.groupby('Maladie'):
        fig_line.add_trace(go.Scatter(x=data['Date'], y=data['Nombre de décès'], mode='lines', name=disease))

    fig_line.update_layout(title='Évolution du nombre de décès par maladie', xaxis_title='Date', yaxis_title='Nombre de décès')
    st.plotly_chart(fig_line)

def get_data_medical_no_death():
    # Connexion à la base de données
    connection = connect_to_mysql(HOST, USER_NAME, PASSWORD, DATABASE)

    if connection:
        # Obtenez le curseur pour exécuter des requêtes SQL
        cursor = connection.cursor()

        # Requête pour obtenir le nombre de cas sans décès par maladie
        cursor.execute("SELECT disease_id, SUM(death_cases) AS total_no_deaths FROM fact_covid_data WHERE Date_id = '9999-01-01' GROUP BY disease_id")
        data_by_disease_no_death = cursor.fetchall()

        # Requête pour obtenir les données par maladie sans décès pour le graphique de ligne
        cursor.execute("SELECT dim_covid_date.date, dim_covid_disease.disease_type, SUM(fact_covid_data.death_cases) AS total_no_deaths FROM fact_covid_data JOIN dim_covid_date ON fact_covid_data.Date_id = dim_covid_date.date JOIN dim_covid_disease ON fact_covid_data.disease_id = dim_covid_disease.disease_type WHERE Date_id = '9999-01-01' GROUP BY dim_covid_date.date, dim_covid_disease.disease_type ORDER BY dim_covid_date.date")
        data_for_line_chart_no_death = cursor.fetchall()

        # Fermer la connexion lorsque vous avez terminé
        close_connection(connection)

        return data_by_disease_no_death, data_for_line_chart_no_death
    else:
        st.error("Impossible de se connecter à la base de données.")

def display_medical_page_no_death():
    st.title("Cas sans décès")

    # Obtenir les données
    data_by_disease_no_death, _ = get_data_medical_no_death()

    # Convertir les résultats des requêtes en DataFrame
    df_by_disease_no_death = pd.DataFrame(data_by_disease_no_death, columns=['Maladie', 'Nombre de cas sans décès'])

    # Affichage du graphique en secteurs (pie chart) du nombre de cas sans décès par maladie
    fig_pie_no_death = px.pie(df_by_disease_no_death, values='Nombre de cas sans décès', names='Maladie', title='Nombre de cas sans décès par maladie')
    st.plotly_chart(fig_pie_no_death)

    # Affichage du graphique à barres du nombre de cas sans décès par maladie
    fig_bar_no_death = px.bar(df_by_disease_no_death, x='Maladie', y='Nombre de cas sans décès', title='Nombre de cas sans décès par maladie')
    st.plotly_chart(fig_bar_no_death)

def get_data_design_by_sex_date():
    # Connexion à la base de données
    connection = connect_to_mysql(HOST, USER_NAME, PASSWORD, DATABASE)

    if connection:
        # Obtenez le curseur pour exécuter des requêtes SQL
        cursor = connection.cursor()

        # Requête pour obtenir le nombre de décès par sexe et par date
        cursor.execute("SELECT Date_id, gender_id, COUNT(death_cases) AS total_deaths FROM fact_covid_data where Date_id != '9999-01-01' GROUP BY Date_id, gender_id")
        data_sex_date = cursor.fetchall()

        # Fermer la connexion lorsque vous avez terminé
        close_connection(connection)

        return data_sex_date
    else:
        st.error("Impossible de se connecter à la base de données.")

def get_data_design_by_sex_total_deaths():
    # Connect to the database
    connection = connect_to_mysql(HOST, USER_NAME, PASSWORD, DATABASE)

    if connection:
        # Get the cursor to execute SQL queries
        cursor = connection.cursor()

        # Execute SQL query to get total deaths by sex
        cursor.execute("SELECT gender_id, SUM(death_cases) AS total_deaths FROM fact_covid_data GROUP BY gender_id")
        data_total_deaths_by_sexe = cursor.fetchall()

        # Close the connection when finished
        close_connection(connection)

        return data_total_deaths_by_sexe
    else:
        st.error("Unable to connect to the database.")

def get_data_design_by_sex_total_cases_without_deaths():
    # Connect to the database
    connection = connect_to_mysql(HOST, USER_NAME, PASSWORD, DATABASE)

    if connection:
        # Get the cursor to execute SQL queries
        cursor = connection.cursor()

        # Execute SQL query to get total cases without deaths by sex
        cursor.execute("SELECT gender_id, SUM(death_cases) AS total_cases_without_deaths FROM fact_covid_data WHERE Date_id = '9999-01-01' GROUP BY gender_id")
        data_total_cases_without_deaths_by_sexe = cursor.fetchall()

        # Close the connection when finished
        close_connection(connection)

        return data_total_cases_without_deaths_by_sexe
    else:
        st.error("Unable to connect to the database.")

def get_death_design_by_age_date():
    # Connexion à la base de données
    connection = connect_to_mysql(HOST, USER_NAME, PASSWORD, DATABASE)

    if connection:
        # Obtenez le curseur pour exécuter des requêtes SQL
        cursor = connection.cursor()

        # Requête pour obtenir le nombre de décès par âge et par date
        cursor.execute("SELECT Date_id, age_id, COUNT(death_cases) AS total_deaths FROM fact_covid_data where Date_id != '9999-01-01' GROUP BY Date_id, age_id")
        data_age_date = cursor.fetchall()

        # Fermer la connexion lorsque vous avez terminé
        close_connection(connection)

        return data_age_date
    else:
        st.error("Impossible de se connecter à la base de données.")

def get_all_cases_design_by_age_date():
    # Connexion à la base de données
    connection = connect_to_mysql(HOST, USER_NAME, PASSWORD, DATABASE)

    if connection:
        # Obtenez le curseur pour exécuter des requêtes SQL
        cursor = connection.cursor()

        # Requête pour obtenir le nombre de décès par âge et par date
        cursor.execute("SELECT age_id, COUNT(death_cases) AS total_deaths FROM fact_covid_data GROUP BY age_id")
        data_age_date = cursor.fetchall()

        # Fermer la connexion lorsque vous avez terminé
        close_connection(connection)

        return data_age_date
    else:
        st.error("Impossible de se connecter à la base de données.")

def display_design_page():
    st.title("Page de conception")

    # Get data for total deaths by sexe
    data_total_deaths_by_sexe = get_data_design_by_sex_total_deaths()  # Define this function to fetch total deaths by sexe
    df_total_deaths_by_sexe = pd.DataFrame(data_total_deaths_by_sexe, columns=['Sexe', 'Nombre de décès'])

    # Get data for total cases without deaths by sexe
    data_total_cases_without_deaths_by_sexe = get_data_design_by_sex_total_cases_without_deaths()  # Define this function to fetch total cases without deaths by sexe
    df_total_cases_without_deaths_by_sexe = pd.DataFrame(data_total_cases_without_deaths_by_sexe, columns=['Sexe', 'Nombre de cas sans décès'])

    # Combine total deaths and total cases without deaths data
    df_total_cases_with_deaths_by_sexe = df_total_deaths_by_sexe.merge(df_total_cases_without_deaths_by_sexe, on='Sexe')

    # Create pie chart for total deaths by sexe
    fig_total_deaths_by_sexe = px.pie(df_total_deaths_by_sexe, values='Nombre de décès', names='Sexe', title='Total Deaths by Sexe')
    st.plotly_chart(fig_total_deaths_by_sexe)

    # Create pie chart for total cases without deaths by sexe
    fig_total_cases_without_deaths_by_sexe = px.pie(df_total_cases_without_deaths_by_sexe, values='Nombre de cas sans décès', names='Sexe', title='Total Cases without Deaths by Sexe')
    st.plotly_chart(fig_total_cases_without_deaths_by_sexe)

    # Create pie chart for total cases with and without deaths by sexe
    fig_total_cases_with_deaths_by_sexe = go.Figure(data=[
        go.Pie(labels=df_total_cases_with_deaths_by_sexe['Sexe'], values=df_total_cases_with_deaths_by_sexe['Nombre de décès'], name='Deaths'),
        go.Pie(labels=df_total_cases_with_deaths_by_sexe['Sexe'], values=df_total_cases_with_deaths_by_sexe['Nombre de cas sans décès'], name='Cases without Deaths')
    ])
    fig_total_cases_with_deaths_by_sexe.update_traces(hole=.4, hoverinfo="label+percent+name")
    fig_total_cases_with_deaths_by_sexe.update_layout(title='Total Cases with and without Deaths by Sexe')
    st.plotly_chart(fig_total_cases_with_deaths_by_sexe)

    # Obtenir les données par sexe et par date
    data_sex_date = get_data_design_by_sex_date()
    df_sex_date = pd.DataFrame(data_sex_date, columns=['Date', 'Sexe', 'Nombre de décès'])

    # Affichage du graphique pour le nombre de décès par sexe et par date
    fig_sex_date = px.line(df_sex_date, x='Date', y='Nombre de décès', color='Sexe', title='Nombre de décès par sexe et par date')
    st.plotly_chart(fig_sex_date)

    # Obtenir les données par âge et par date
    data_age_date = get_death_design_by_age_date()
    all_data_age_date = get_all_cases_design_by_age_date()
    df_age_date = pd.DataFrame(data_age_date, columns=['Date', 'Âge', 'Nombre de décès'])
    all_df_age_date = pd.DataFrame(all_data_age_date, columns=['Âge', 'Nombre total de cas'])

    # Affichage du graphique pour le nombre de décès par âge et par date avec des couleurs alternatives pour chaque âge
    fig_age_date = px.bar(df_age_date, x='Date', y='Nombre de décès', color='Âge', title='Nombre de décès par âge et par date')
    st.plotly_chart(fig_age_date)

    # Affichage du graphique à barres pour le nombre total de cas par âge et par date
    fig_bar_all_cases_by_age_date = px.bar(all_df_age_date, x='Âge', y='Nombre total de cas',
                                           title='Nombre total de cas par âge')
    st.plotly_chart(fig_bar_all_cases_by_age_date)

def get_data_simple_total_cases_by_year():
    # Connexion à la base de données
    connection = connect_to_mysql(HOST, USER_NAME, PASSWORD, DATABASE)

    if connection:
        # Obtenez le curseur pour exécuter des requêtes SQL
        cursor = connection.cursor()

        # Requête pour obtenir le nombre total de cas par année
        cursor.execute("SELECT YEAR(Date_id) AS Annee, COUNT(*) AS Nombre_de_cas FROM fact_covid_data where Date_id!='9999-01-01' GROUP BY YEAR(Date_id)")
        data_by_year = cursor.fetchall()

        # Fermer la connexion lorsque vous avez terminé
        close_connection(connection)

        return data_by_year
    else:
        st.error("Impossible de se connecter à la base de données.")

def get_total_cases_count():
    # Connexion à la base de données
    connection = connect_to_mysql(HOST, USER_NAME, PASSWORD, DATABASE)

    if connection:
        # Obtenez le curseur pour exécuter des requêtes SQL
        cursor = connection.cursor()

        # Requête pour obtenir le nombre total de cas dans la table
        cursor.execute("SELECT COUNT(*) FROM fact_covid_data")
        total_cases_count = cursor.fetchone()[0]  # Obtenir le résultat de la requête

        # Fermer la connexion lorsque vous avez terminé
        close_connection(connection)

        return total_cases_count
    else:
        st.error("Impossible de se connecter à la base de données.")


def display_simple_page():
    st.title("Page simple")

    # Obtenir le nombre total de cas dans un cadre carré au milieu de la page
    total_cases_count = get_total_cases_count()

    st.markdown("---")  # Ajouter une ligne horizontale pour séparer
    st.write("")  # Ajouter un espace

    # Centrer le message "Nombre total de cas : 78047"
    st.markdown(f"<h1 style='text-align:center;'>Nombre total de cas : <b>{total_cases_count}</b></h1>",
                unsafe_allow_html=True)

    st.write("")  # Ajouter un espace
    st.markdown('---')  # Ajouter une ligne horizontale pour séparer

    # Obtenir les données pour le nombre total de cas par année
    data_total_cases_by_year = get_data_simple_total_cases_by_year()
    df_total_cases_by_year = pd.DataFrame(data_total_cases_by_year, columns=['Année', 'Nombre de cas'])

    # Créer un graphique à barres pour le nombre total de cas par année
    fig_total_cases_by_year = px.bar(df_total_cases_by_year, x='Année', y='Nombre de cas',
                                     title='Total des décès par année')
    st.plotly_chart(fig_total_cases_by_year)


def main():
    user = st.session_state.user

    if not user:
        login()
    else:
        st.title("Page principale")
        st.write("Bienvenue,", user[0])  # Affichez le nom de l'utilisateur par exemple
        # Affichez ici le contenu de votre page principale après la connexion réussie
        work = user[2]
        if work == "Medical":
            st.write("Contenu spécifique pour les utilisateurs du domaine médical")
            display_medical_page()
            display_medical_page_no_death()
        elif work == "Design":
            st.write("Contenu spécifique pour les utilisateurs du domaine du design")
            display_design_page()
        elif work == "Simple":
            st.write("Contenu général pour tous les utilisateurs")
            display_simple_page()

if __name__ == "__main__":
    main()
