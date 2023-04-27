import os
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title='GUI - Análise', layout='wide', page_icon='📉')
st.title("Análise de medições dos transformadores - AL02059122")
st.markdown('Desenvolvida por Ana Camila Mamede')

tick_font_size = 20 
axis_font_size = 22
legend_font_size = 18
d_tick = 2

def file_selector(folder_path): 
    st.sidebar.markdown('### Escolha do arquivo')
    with st.sidebar:
        all_files = os.listdir(folder_path)
        filenames = list()
        i = 0
        while i < len(all_files):
            if "TRANSFORMADOR" in (all_files[i]):
                filenames.append(all_files[i])
            i += 1

        # selected_filename = st.selectbox('Selecione um arquivo referência:', filenames, disabled=False)
        selected_filename = st.radio( 'Selecione um arquivo:',options = filenames, disabled=False)
        file = os.path.join(folder_path, selected_filename)

    return file,selected_filename

def data_preparation(df, Vbase, Sn):
    # Data Preparation
    df['Registro'] = pd.to_datetime(df['Registro'],format='%d/%m/%Y %H:%M')
    df['data'] = df['Registro'].apply(lambda x: x.date())
    df['dia'] = df['Registro'].apply(lambda x: x.day)
    df['horario'] = df['Registro'].apply(lambda x: x.time())
    df['hora'] = df['Registro'].apply(lambda x: x.hour)

    df_max = df[['Van [V]', 'Vbn [V]', 'Vcn [V]','S [VA]','dia','hora']].groupby(['dia','hora']).max().reset_index().rename(columns={'Van [V]':'Van_max [pu]', 'Vbn [V]':'Vbn_max [pu]', 'Vcn [V]':'Vcn_max [pu]','S [VA]':'S_max [kVA]'})
    df_max[['Van_max [pu]', 'Vbn_max [pu]', 'Vcn_max [pu]']] = df_max[['Van_max [pu]', 'Vbn_max [pu]', 'Vcn_max [pu]']]/Vbase
    df_max['S_max [kVA]'] = df_max['S_max [kVA]']/1000

    df_min = df[['Van [V]', 'Vbn [V]', 'Vcn [V]','S [VA]','dia','hora']].groupby(['dia','hora']).min().reset_index().rename(columns={'Van [V]':'Van_min [pu]', 'Vbn [V]':'Vbn_min [pu]', 'Vcn [V]':'Vcn_min [pu]','S [VA]':'S_min [kVA]'})
    df_min[['Van_min [pu]', 'Vbn_min [pu]', 'Vcn_min [pu]']] = df_min[['Van_min [pu]', 'Vbn_min [pu]', 'Vcn_min [pu]']]/Vbase
    df_min['S_min [kVA]'] = df_min['S_min [kVA]']/1000

    df_final = pd.merge(df_max,df_min, on=['dia','hora'],how='inner')
    df_final['Carregamento'] = df_final['S_max [kVA]']/Sn

    return df_final

def grafico_carregamento(df_final,dia):
    aux = df_final[df_final['dia']==dia]
    fig = px.line(aux,x='hora', y=['Carregamento'])
    fig.update_xaxes(dtick=d_tick,showgrid=True)
    fig.update_layout(title='<b>Carregamento no dia {} - {}<b>'.format(dia,trafo),xaxis_title='Hora do dia', yaxis_title='Carregamento [pu]',showlegend=False,font=dict(size=20))
    fig.update_layout(title=dict(font = dict(size=axis_font_size+2)), legend_title = dict(font = dict(size=legend_font_size+2)), 
                        font=dict(size=18), xaxis = dict( tickfont = dict(size=tick_font_size)), yaxis = dict( tickfont = dict(size=tick_font_size)), 
                        xaxis_title= dict( font = dict(size=axis_font_size)), yaxis_title= dict( font = dict(size=axis_font_size)),legend = dict(font = dict(size=legend_font_size)))
    return fig

def grafico_carregamento_completo(df_final):
    aux2 = df_final.copy()
    aux2['dia'] = aux2['dia'].apply(lambda x: str(x))
    aux2['hora'] = aux2['hora'].apply(lambda x: str(x))
    aux2['dia_hora'] = aux2['dia'] + '_' + aux2['hora']+'h'
    fig = px.line(aux2,x='dia_hora', y=['Carregamento'])
    fig.update_xaxes(dtick=d_tick+2,showgrid=True)
    fig.update_layout(title='<b>Carregamento - {}<b>'.format(trafo),xaxis_title='Dia_hora', yaxis_title='Carregamento [pu]',showlegend=False,font=dict(size=20))
    fig.update_layout(title=dict(font = dict(size=axis_font_size+2)), legend_title = dict(font = dict(size=legend_font_size+2)), 
                        font=dict(size=18), xaxis = dict( tickfont = dict(size=tick_font_size)), yaxis = dict( tickfont = dict(size=tick_font_size)), 
                        xaxis_title= dict( font = dict(size=axis_font_size)), yaxis_title= dict( font = dict(size=axis_font_size)),legend = dict(font = dict(size=legend_font_size)))
    return fig

def grafico_tensao_max(df_final,dia):
    aux = df_final[df_final['dia']==dia]
    fig = px.line(aux,x='hora', y=['Van_max [pu]', 'Vbn_max [pu]', 'Vcn_max [pu]'])
    fig.update_xaxes(dtick=d_tick,showgrid=True)
    fig.update_layout(title='<b>Tensão máxima no dia {} - {}<b>'.format(dia,trafo),xaxis_title='Hora do dia', yaxis_title='Tensão [pu]',legend_title='',font=dict(size=20)) 
    fig.update_layout(title=dict(font = dict(size=axis_font_size+2)), legend_title = dict(font = dict(size=legend_font_size+2)), 
                        font=dict(size=18), xaxis = dict( tickfont = dict(size=tick_font_size)), yaxis = dict( tickfont = dict(size=tick_font_size)), 
                        xaxis_title= dict( font = dict(size=axis_font_size)), yaxis_title= dict( font = dict(size=axis_font_size)),legend = dict(font = dict(size=legend_font_size),x=0.3,y=0.1,orientation="h")) #,x=0,y=0.1,orientation="h"
    return fig

def grafico_tensao_max_completo(df_final):
    aux2 = df_final.copy()
    aux2['dia'] = aux2['dia'].apply(lambda x: str(x))
    aux2['hora'] = aux2['hora'].apply(lambda x: str(x))
    aux2['dia_hora'] = aux2['dia'] + '_' + aux2['hora']+'h'
    fig = px.line(aux2,x='dia_hora', y=['Van_max [pu]', 'Vbn_max [pu]', 'Vcn_max [pu]'])
    fig.update_xaxes(dtick=d_tick+2,showgrid=True)
    fig.update_layout(title='<b>Tensão máxima - {}<b>'.format(trafo),xaxis_title='Dia_hora', yaxis_title='Tensão [pu]',legend_title='',font=dict(size=20)) 
    fig.update_layout(title=dict(font = dict(size=axis_font_size+2)), legend_title = dict(font = dict(size=legend_font_size+2)), 
                        font=dict(size=18), xaxis = dict( tickfont = dict(size=tick_font_size)), yaxis = dict( tickfont = dict(size=tick_font_size)), 
                        xaxis_title= dict( font = dict(size=axis_font_size)), yaxis_title= dict( font = dict(size=axis_font_size)),legend = dict(font = dict(size=legend_font_size),x=0.3,y=0.1,orientation="h"))
    return fig

def grafico_tensao_min(df_final,dia):
    aux = df_final[df_final['dia']==dia]
    fig = px.line(aux,x='hora', y=['Van_min [pu]', 'Vbn_min [pu]', 'Vcn_min [pu]'])
    fig.update_xaxes(dtick=d_tick,showgrid=True)
    fig.update_layout(title='<b>Tensão mínima no dia {} - {}<b>'.format(dia,trafo),xaxis_title='Hora do dia', yaxis_title='Tensão [pu]',legend_title='',font=dict(size=20))    
    fig.update_layout(title=dict(font = dict(size=axis_font_size+2)), legend_title = dict(font = dict(size=legend_font_size+2)), 
                        font=dict(size=18), xaxis = dict( tickfont = dict(size=tick_font_size)), yaxis = dict( tickfont = dict(size=tick_font_size)), 
                        xaxis_title= dict( font = dict(size=axis_font_size)), yaxis_title= dict( font = dict(size=axis_font_size)),legend = dict(font = dict(size=legend_font_size),x=0.3,y=0.1,orientation="h"))

    return fig

def grafico_tensao_min_completo(df_final):
    aux2 = df_final.copy()
    aux2['dia'] = aux2['dia'].apply(lambda x: str(x))
    aux2['hora'] = aux2['hora'].apply(lambda x: str(x))
    aux2['dia_hora'] = aux2['dia'] + '_' + aux2['hora']+'h'
    fig = px.line(aux2,x='dia_hora', y=['Van_min [pu]', 'Vbn_min [pu]', 'Vcn_min [pu]'])
    fig.update_xaxes(dtick=d_tick+2,showgrid=True)
    fig.update_layout(title='<b>Tensão mínima - {}<b>'.format(trafo),xaxis_title='Dia_hora', yaxis_title='Tensão [pu]',legend_title='',font=dict(size=20))    
    fig.update_layout(title=dict(font = dict(size=axis_font_size+2)), legend_title = dict(font = dict(size=legend_font_size+2)), 
                        font=dict(size=18), xaxis = dict( tickfont = dict(size=tick_font_size)), yaxis = dict( tickfont = dict(size=tick_font_size)), 
                        xaxis_title= dict( font = dict(size=axis_font_size)), yaxis_title= dict( font = dict(size=axis_font_size)),legend = dict(font = dict(size=legend_font_size),x=0.3,y=0.1,orientation="h"))
    return fig



if __name__ == '__main__':
    folder_path = "datasets/"
    file,selected_filename = file_selector(folder_path)
    trafo = selected_filename.replace('.csv','')

    df_gd = pd.read_csv(os.path.join(folder_path, 'mini-micro-bt.csv'))
    df_gd['cod_trafo'] = df_gd['cod_trafo'].apply(lambda x: str(x))
    df_gd['id_trafo'] = df_gd['id_trafo'].apply(lambda x: str(x))
    df_gd['Snom'] = df_gd['Snom'].str.replace(',','.').astype(float)

    st.sidebar.markdown('### Valores Base:')
    Sn = st.sidebar.number_input('S (kVA)',value=150.0,step=0.5)
    Vbase = st.sidebar.number_input('Tensão F-N (V)',value=220)

    df = pd.read_csv(file)
    df_final = data_preparation(df, Vbase, Sn)

    selected = option_menu( menu_title=None, 
                       options=['Visualização dos dados', 'Gráficos'],
                       icons = ['table', 'bar-chart-fill'],
                       orientation='horizontal')


    if selected=='Visualização dos dados':
        st.markdown('## Resumo')  
        c1, c2 = st.columns([1,1])
        resumo = df[['Van [V]', 'Vbn [V]', 'Vcn [V]','S [VA]','Registro']].agg([min, max]).T  
        c1.markdown('### Medições')      
        c1.dataframe(resumo, width=350)      
        c2.markdown('### Geração Distribuída')  
        res_gd = df_gd.loc[df_gd['cod_trafo'].isin(['5700047122', '5700154122', '5700182122', '5703368122', '5703992122',
                                                    '5704615122', '5707288122'])].sort_values('POT_INST_GD',ascending=False).reset_index()
        c2.dataframe(res_gd, width=600)    

        st.markdown('## Dados:')
        st.markdown('Clique no nome coluna para ordenar')
        st.dataframe(df_final.style.highlight_min(color = 'yellow', subset=['Van_max [pu]', 'Vbn_max [pu]', 'Vcn_max [pu]',
       'S_max [kVA]', 'Van_min [pu]', 'Vbn_min [pu]', 'Vcn_min [pu]','S_min [kVA]', 'Carregamento']).highlight_max(color = 'red', subset=['Van_max [pu]', 'Vbn_max [pu]', 'Vcn_max [pu]',
       'S_max [kVA]', 'Van_min [pu]', 'Vbn_min [pu]', 'Vcn_min [pu]','S_min [kVA]', 'Carregamento']),height=500)
    
    if selected=='Gráficos':
        st.markdown('## Gráficos 24h')
        # dia = st.number_input('Escolha o dia', value=df_final['dia'][0])
        dia = st.selectbox('Escolha o dia:', df_final['dia'].unique())

        # Carregamento
        fig_c = grafico_carregamento(df_final,dia)
        st.plotly_chart(fig_c, use_container_width=True)

        # Tensão
        fig_v1 = grafico_tensao_max(df_final,dia)
        st.plotly_chart(fig_v1, use_container_width=True)
        fig_v2 = grafico_tensao_min(df_final,dia)
        st.plotly_chart(fig_v2, use_container_width=True)

        completo = st.checkbox('Visualizar gráficos completos', value=True)
        if completo:
            fig_s = grafico_carregamento_completo(df_final)
            st.plotly_chart(fig_s, use_container_width=True)
            fig_v1 = grafico_tensao_max_completo(df_final)
            st.plotly_chart(fig_v1, use_container_width=True)
            fig_v2 = grafico_tensao_min_completo(df_final)
            st.plotly_chart(fig_v2, use_container_width=True)

