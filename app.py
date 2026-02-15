import streamlit as st
from streamlit_folium import st_folium
import osmnx as ox
import networkx as nx
import folium
from folium.plugins import AntPath

# 1. Configuração da Página
st.set_page_config(page_title="Simulador de Rotas | Basestar OS", layout="wide")

st.title("🛰️ Simulador de Algoritmos Urbanos")
st.markdown("---")

# 2. Inicialização da Memória de Sessão
if 'mapa_dinamico' not in st.session_state:
    st.session_state.mapa_dinamico = None

# 3. Sidebar com Inputs Atualizados
with st.sidebar:
    st.header("📍 Parâmetros do Percurso")
    
    st.subheader("Coordenadas de Partida")
    lat_ini = st.number_input("Latitude", value=-12.2568, format="%.4f")
    lon_ini = st.number_input("Longitude", value=-38.9532, format="%.4f")
    
    st.subheader("Coordenadas de Destino")
    lat_fim = st.number_input("Latitude", value=-12.2003, format="%.4f")
    lon_fim = st.number_input("Longitude", value=-38.9712, format="%.4f")
    
    # Atualização: Unidade em KM com máximo de 5000
    distancia_km = st.slider("Raio de Busca (km)", min_value=1, max_value=20, value=8)
    
    executar = st.button('🚀 Processar Algoritmo A*')

# 4. Função de Cálculo (Conversão KM -> Metros interna)
@st.cache_data
def calcular_rota_custom(p1, p2, raio_km):
    try:
        # Conversão para metros, pois o OSMnx trabalha com essa unidade
        raio_metros = raio_km * 1000 
        
        centro = ((p1[0] + p2[0])/2, (p1[1] + p2[1])/2)
        G = ox.graph_from_point(centro, dist=raio_metros, network_type='drive')
        
        orig_node = ox.distance.nearest_nodes(G, p1[1], p1[0])
        dest_node = ox.distance.nearest_nodes(G, p2[1], p2[0])
        
        path = nx.astar_path(G, orig_node, dest_node, weight='length')
        return [(G.nodes[node]['y'], G.nodes[node]['x']) for node in path]
    except Exception as e:
        st.error(f"Erro: O raio de {raio_km}km pode ser grande demais para o servidor de mapas ou a conexão falhou. Detalhes: {e}")
        return None

# 5. Lógica de Execução
if executar:
    p_inicio = (lat_ini, lon_ini)
    p_fim = (lat_fim, lon_fim)
    
    with st.spinner(f'Mapeando grafos em um raio de {distancia_km}km...'):
        coords = calcular_rota_custom(p_inicio, p_fim, distancia_km)
        
        if coords:
            m = folium.Map(location=[lat_ini, lon_ini], zoom_start=13, tiles='CartoDB dark_matter')

            for coord in coords[::2]:
                folium.CircleMarker(location=coord, radius=8, color='#00ffff', fill=True, fill_color='#00ffff', fill_opacity=0.2, weight=0).add_to(m)
                folium.CircleMarker(location=coord, radius=2, color='#ffffff', fill=True, fill_color='#ffffff', fill_opacity=1, weight=0).add_to(m)

            AntPath(locations=coords, dash_array=[1, 20], delay=600, color='#00ffff', pulse_color='#ffffff', weight=3, opacity=0.5).add_to(m)
            st.session_state.mapa_dinamico = m

# 6. Exibição
if st.session_state.mapa_dinamico:
    st_folium(st.session_state.mapa_dinamico, width=1100, height=600, key="mapa_view_km")