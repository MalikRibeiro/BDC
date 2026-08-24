# ESTRUTURA

BDC
├── docs
│   ├── backlog_bd_credito.md
│   └── planejamento_sistema_bd_credito_operacional_v1_2.pdf
├── ENTRADAS
│   ├── atualizacoes_manuais
│   │   └── pendentes
│   ├── blacklist
│   ├── configs
│   │   ├── app_config.json
│   │   └── config.json
│   ├── contratos_denodo
│   │   └── com-query-1786383902283.csv
│   ├── control
│   │   ├── configs
│   │   │   ├── pd_cpura_config.json
│   │   │   ├── pd_faixas.json
│   │   │   └── score_cpura_config.json
│   │   ├── layouts
│   │   │   ├── catalogo_layouts_ficha_comercializadora.json
│   │   │   ├── catalogo_layouts_ficha_consumidor.json
│   │   │   ├── layout_ficha_comercializadora_v1.json
│   │   │   ├── layout_ficha_comercializadora_v2.json
│   │   │   ├── layout_ficha_comercializadora_v3.json
│   │   │   ├── layout_ficha_comercializadora_v4.json
│   │   │   ├── layout_ficha_comercializadora_v5.json
│   │   │   ├── layout_ficha_comercializadora_v6.json
│   │   │   ├── layout_ficha_comercializadora_v7.json
│   │   │   ├── layout_ficha_consumidor_v1.json
│   │   │   ├── layout_ficha_consumidor_v2.json
│   │   │   └── layout_ficha_consumidor_v3.json
│   │   ├── mappings
│   │   │   ├── mapping_fichas_comercializadoras.json
│   │   │   └── mapping_fichas_consumidores.json
│   │   ├── quality
│   │   │   ├── data_quality_rules_fichas_consumidores.json
│   │   │   ├── domain_dictionaries.json
│   │   │   ├── field_types_fichas_consumidores.json
│   │   │   ├── master_catalog_comercializadoras.json
│   │   │   └── pk_fk_rules.json
│   │   ├── rules
│   │   │   ├── pd_transform_rules.json
│   │   │   └── rating_qualitativo.json
│   │   └── schemas
│   │       ├── schema_app_config.json
│   │       ├── schema_carga_manual.json
│   │       ├── schema_config.json
│   │       ├── schema_data_quality_rules.json
│   │       ├── schema_ficha_comercializadora_extraida.json
│   │       ├── schema_ficha_consumidor_extraida.json
│   │       ├── schema_ingestion_log.json
│   │       ├── schema_mapping_fichas_comercializadoras.json
│   │       └── schema_mapping_fichas_consumidores.json
│   ├── fichas
│   │   ├── comercializadoras
│   │   │   ├── pendentes
│   │   │   │   ├── 2W ENERGIA 05_07_2022.xlsx
│   │   │   │   ├── 2W ENERGIA_28.08.2024.xlsx
│   │   │   │   ├── 2W_13062023 - Copia.xlsx
│   │   │   │   ├── 2W_18_06_2021.xlsx
│   │   │   │   ├── ABC 29.07.2024.xlsx
│   │   │   │   ├── ABC BRASIL 15102025.xlsx
│   │   │   │   ├── AES BRASIL 09_05_2022 TESTE GRUPO.xlsx
│   │   │   │   ├── AES_05012024.xlsx
│   │   │   │   ├── AES_19.06.2024.xlsx
│   │   │   │   ├── AGORA21.05.2024.xlsx
│   │   │   │   ├── AGROENERGIA _10_05_2021.xlsx
│   │   │   │   ├── ALCAST_12.07.2024.xlsx
│   │   │   │   ├── ALIANÇA 20_07_2022.xlsx
│   │   │   │   ├── ALUPAR 19112024.xlsx
│   │   │   │   ├── ALUPAR_06062025.xlsx
│   │   │   │   ├── AMAGGI 11_07_2022.xlsx
│   │   │   │   ├── AMAGGI 26062025.xlsx
│   │   │   │   ├── AMBAR 11122023.xlsx
│   │   │   │   ├── AMBAR 26_04_2022.xlsx
│   │   │   │   ├── AMBAR_29.07.2024.xlsx
│   │   │   │   ├── AMBAR_31_08_2021.xlsx
│   │   │   │   ├── AMERICA_07_06_2021.xlsx
│   │   │   │   ├── AMERICA_20.05.2024.xlsx
│   │   │   │   ├── APOLLO 08 05 2024.xlsx
│   │   │   │   ├── APOLO 02_05_2022.xlsx
│   │   │   │   ├── APOLO_24_06_2021.xlsx
│   │   │   │   ├── APTCOM_10052023.xlsx
│   │   │   │   ├── ARCELORMITTAL_21.05.2024.xlsx
│   │   │   │   ├── ARMOR 15082025.xlsx
│   │   │   │   ├── ARMOR_20.05.2024.xlsx
│   │   │   │   ├── ARMOS_07062023.xlsx
│   │   │   │   ├── ATHENA 29_08_2022.xlsx
│   │   │   │   ├── ATIAIA 24062025.xlsx
│   │   │   │   ├── ATLAS_18022025.xlsx
│   │   │   │   ├── ATMO 06_05_2022.xlsx
│   │   │   │   ├── ATMO 16052025.xlsx
│   │   │   │   ├── ATMO 16052025__1.xlsx
│   │   │   │   ├── ATMO_06.06.2024.xlsx
│   │   │   │   ├── ATMO_16062023.xlsx
│   │   │   │   ├── ATMO_31_08_2021.xlsx
│   │   │   │   ├── AUREN (VOTENER) 06_05_2022.xlsx
│   │   │   │   ├── AUREN_13.06.2024.xlsx
│   │   │   │   ├── AUREN_16062023.xlsx
│   │   │   │   ├── AUREN_24092025.xlsx
│   │   │   │   ├── B2R 27_06_2022.xlsx
│   │   │   │   ├── B2R ENERGIA_20122021.xlsx
│   │   │   │   ├── B2R_06.06.2024.xlsx
│   │   │   │   ├── B2R_22.05.2024.xlsx
│   │   │   │   ├── Banco ABC 05092023.xlsx
│   │   │   │   ├── BANCO BOCOM BBM 25_05_2022.xlsx
│   │   │   │   ├── BANCO BTG PACTUAL (GRUPO) 14_07_2022.xlsx
│   │   │   │   ├── BARIGUI_17.05.2024.xlsx
│   │   │   │   ├── BARIGUI_17032023.xlsx
│   │   │   │   ├── BC 06_05_2022.xlsx
│   │   │   │   ├── BC COMERCIALIZADORA 27032026.xlsx
│   │   │   │   ├── BC_05042024.xlsx
│   │   │   │   ├── BEP 08_06_2022.xlsx
│   │   │   │   ├── BEP 09072025 - Copia.xlsx
│   │   │   │   ├── BEP 31_08_2021.xlsx
│   │   │   │   ├── BEP_16.05.2024.xlsx
│   │   │   │   ├── BID ENERGY 04_05_2022.xlsx
│   │   │   │   ├── BID_12.06.2024.xlsx
│   │   │   │   ├── BID_13102023.xlsx
│   │   │   │   ├── BO ENERGY 04_05_2022.xlsx
│   │   │   │   ├── BOENERGY_08052023.xlsx
│   │   │   │   ├── BOLT 05092023.xlsx
│   │   │   │   ├── BOLT 06_06_2022.xlsx
│   │   │   │   ├── BOLT_01_09_2021.xlsx
│   │   │   │   ├── BOLT_17.05.2024.xlsx
│   │   │   │   ├── BOLT_2024.xlsx
│   │   │   │   ├── BOREAL 17_05_2022.xlsx
│   │   │   │   ├── BOREAL_01_09_2021.xlsx
│   │   │   │   ├── BOVEN 27_06_2022.xlsx
│   │   │   │   ├── BOVEN 28032024.xlsx
│   │   │   │   ├── BP COM_04_10_2021.xlsx
│   │   │   │   ├── BP Comercializadora_28_01_2022.xlsx
│   │   │   │   ├── BP ENERGIA_23.07.2024.xlsx
│   │   │   │   ├── BR ENERGIAS RATING 03022026.xlsx
│   │   │   │   ├── BRADESCO 04072025.xlsx
│   │   │   │   ├── BRASIL COM 11_07_2022.xlsx
│   │   │   │   ├── BRASIL COM_11_06_2021.xlsx
│   │   │   │   ├── BRASIL COM_18_04_2023.xlsx
│   │   │   │   ├── BRASIL SERVICOS_08_06_2021.xlsx
│   │   │   │   ├── BRASIL Serviços_18042023.xlsx
│   │   │   │   ├── BRASKEN 19 04 2024.xlsx
│   │   │   │   ├── BRAVO 11042024.xlsx
│   │   │   │   ├── Bravo_2024 (Salvo automaticamente).xlsx
│   │   │   │   ├── BRAVO_25_10_2021.xlsx
│   │   │   │   ├── BRAVO_26052023.xlsx
│   │   │   │   ├── BRF Energia 15072025.xlsx
│   │   │   │   ├── BROOKFIELD_01_09_2021.xlsx
│   │   │   │   ├── BROOKFILD 04_05_2022.xlsx
│   │   │   │   ├── BTG 01102024.xlsx
│   │   │   │   ├── BTG 15102025.xlsx
│   │   │   │   ├── BTG PACTUAL (BANCO)_08-11_2021.xlsx
│   │   │   │   ├── BTG_05092023.xlsx
│   │   │   │   ├── BTG_29.07.2024.xlsx
│   │   │   │   ├── CANADIAN RATING 21012026.xlsx
│   │   │   │   ├── CANADIAN SOLAR_06_10_2022.xlsx
│   │   │   │   ├── CANADIAN_17042023.xlsx
│   │   │   │   ├── CAPITALE 01102025.xlsx
│   │   │   │   ├── CAPITALE 30_05_2022.xlsx
│   │   │   │   ├── CAPITALE_16062023.xlsx
│   │   │   │   ├── CAPITALE_26.06.2024.xlsx
│   │   │   │   ├── CASA DOS VENTOS 03 05 2024.xlsx
│   │   │   │   ├── CASA DOS VENTOS 08_06_2022.xlsx
│   │   │   │   ├── CASA DOS VENTOS RATING 29102025.xlsx
│   │   │   │   ├── CASA_DOS_VENTOS_11082023.xlsx
│   │   │   │   ├── CASTROLANDA 01042024.xlsx
│   │   │   │   ├── CASTROLANDA 10122025.xlsx
│   │   │   │   ├── CEI 10092025.xlsx
│   │   │   │   ├── CELESC 11_05_2022.xlsx
│   │   │   │   ├── CELESC_16042024.xlsx
│   │   │   │   ├── CEMIG 05-07-2024 trading.xlsx
│   │   │   │   ├── CEMIG H COMERCIALIZAÇÃO_23_02_2022.xlsx
│   │   │   │   ├── CEMIG_09062023.xlsx
│   │   │   │   ├── CEMIG_13.06.2024.xlsx
│   │   │   │   ├── CEMIG_24092025.xlsx
│   │   │   │   ├── CENTRAL 06_05_2022.xlsx
│   │   │   │   ├── CENTRAL 08 05 2024.xlsx
│   │   │   │   ├── Central_22_05_2025.xlsx
│   │   │   │   ├── CERCAR SA RATING 12022026.xlsx
│   │   │   │   ├── CGN 05122025.xlsx
│   │   │   │   ├── CGN_30.07.2024.xlsx
│   │   │   │   ├── CGN_30102023.xlsx
│   │   │   │   ├── COMEL 18062025.xlsx
│   │   │   │   ├── COMEL_2023.xlsx
│   │   │   │   ├── COMERC 13_06_2022.xlsx
│   │   │   │   ├── COMERC 29 04 2024.xlsx
│   │   │   │   ├── COMERC Participações 28112023.xlsx
│   │   │   │   ├── COMERC_19062023.xlsx
│   │   │   │   ├── COPEL_23.07.2024.xlsx
│   │   │   │   ├── COPELCOM_16_04_2021.xlsx
│   │   │   │   ├── COPELGET_27112024.xlsx
│   │   │   │   ├── COTESA 30_05_2022.xlsx
│   │   │   │   ├── COTESA_14_10_2021.xlsx
│   │   │   │   ├── CPFL 04072025.xlsx
│   │   │   │   ├── CPFL 04072025__1.xlsx
│   │   │   │   ├── CPFL_01_06_2022.xlsx
│   │   │   │   ├── CPFL_11.08.2023_.xlsx
│   │   │   │   ├── CPFL_28.08.2024.xlsx
│   │   │   │   ├── CTG 24092025.xlsx
│   │   │   │   ├── CTG BRNE_28.08.2024.xlsx
│   │   │   │   ├── CTG NE 02022024.xlsx
│   │   │   │   ├── CTG Trading_04_06_2021.xlsx
│   │   │   │   ├── CTG Trading_16082023.xlsx
│   │   │   │   ├── CTG trading_28.08.2024.xlsx
│   │   │   │   ├── CZARNIKOW 13062025.xlsx
│   │   │   │   ├── Czarnikow 27-01-2025.xlsx
│   │   │   │   ├── CZARNIKOW 27_09_2022.xlsx
│   │   │   │   ├── CZARNIKOW_07_06_2021 (zerada manualmente).xlsx
│   │   │   │   ├── D3 Comercializadora_18.03.2024.xlsx
│   │   │   │   ├── DANSKE 10072025.xlsx
│   │   │   │   ├── DANSKE 12112024.xlsx
│   │   │   │   ├── DEAL 10_05_2022.xlsx
│   │   │   │   ├── DEAL 16102025.xlsx
│   │   │   │   ├── DEAL 27102023.xlsx
│   │   │   │   ├── DEAL_14_10_2021.xlsx
│   │   │   │   ├── DEAL_26.06.2024.xlsx
│   │   │   │   ├── DELTA 12_04_2022 31 12 2021.xlsx
│   │   │   │   ├── Delta Energia 01072025.xlsx
│   │   │   │   ├── DELTA_19022025.xlsx
│   │   │   │   ├── DESTTRA_02_09_2021.xlsx
│   │   │   │   ├── DIFERENCIAL 13_04_2022.xlsx
│   │   │   │   ├── DIFERENCIAL_02_09_2021.xlsx
│   │   │   │   ├── DIFERENCIAL_16.05.2024.xlsx
│   │   │   │   ├── DIFERENCIAL_20072023.xlsx
│   │   │   │   ├── ECEL - ELETRON_03_09_2021.xlsx
│   │   │   │   ├── Echoenergia Participações.xlsx
│   │   │   │   ├── ECHOENERGIA_09_09_2021.xlsx
│   │   │   │   ├── ECOM 17_05_2022.xlsx
│   │   │   │   ├── ECOM 23112023.xlsx
│   │   │   │   ├── ECOM_11042024.xlsx
│   │   │   │   ├── ECOM_14_10_2021.xlsx
│   │   │   │   ├── ECOM_2024.xlsx
│   │   │   │   ├── EDF 01042026.xlsx
│   │   │   │   ├── EDF 06122023.xlsx
│   │   │   │   ├── EDF VERDECOM 22082025.xlsx
│   │   │   │   ├── EDP_12062023.xlsx
│   │   │   │   ├── EDP_2025.xlsx
│   │   │   │   ├── EEI BARIGUI_04_02_2022 divididos por 12.xlsx
│   │   │   │   ├── EGS_29_08_2024.xlsx
│   │   │   │   ├── EKOA 06_06_2022.xlsx
│   │   │   │   ├── EKOA_03_09_2021.xlsx
│   │   │   │   ├── ELECTRA 26032024.xlsx
│   │   │   │   ├── ELECTRA 29_08_2022.xlsx
│   │   │   │   ├── ELECTRA ENERGY 18_04_2023.xlsx
│   │   │   │   ├── ELECTRA ENERGY_2024.xlsx
│   │   │   │   ├── ELECTRA_02_09_2021.xlsx
│   │   │   │   ├── ELECTRA_15042024.xlsx
│   │   │   │   ├── ELERA COM 31072025.xlsx
│   │   │   │   ├── ELERA_19012024.xlsx
│   │   │   │   ├── ELERA_30.07.2024.xlsx
│   │   │   │   ├── ELETROBRAS_24092025.xlsx
│   │   │   │   ├── ELETRON 30_05_2022.xlsx
│   │   │   │   ├── ENECEL_03_09_2021.xlsx
│   │   │   │   ├── ENECEL_26.06.2024.xlsx
│   │   │   │   ├── ENEL 22_06_2022.xlsx
│   │   │   │   ├── Enel Brasil_25092025.xlsx
│   │   │   │   ├── ENEL TRADING 27112023.xlsx
│   │   │   │   ├── ENEL_29.07.2024.xlsx
│   │   │   │   ├── ENERCORE 07_04_2022.xlsx
│   │   │   │   ├── ENERCORE_11042024.xlsx
│   │   │   │   ├── ENERCORE_2024.xlsx
│   │   │   │   ├── ENERCORE_22032023.xlsx
│   │   │   │   ├── ENERGETICA 03_03_2022.xlsx
│   │   │   │   ├── ENERGISA 07052024.xlsx
│   │   │   │   ├── ENERGISA 30102025.xlsx
│   │   │   │   ├── ENERGISA(GRUPO)_04_09_2021.xlsx
│   │   │   │   ├── ENERGIZOU 17_03_2022.xlsx
│   │   │   │   ├── ENERGIZOU_05.06.2024.xlsx
│   │   │   │   ├── ENERPEIXE COMERCIALIZADORA16092025.xlsx
│   │   │   │   ├── ENEVA 30102025.xlsx
│   │   │   │   ├── ENEVA_05042023.xlsx
│   │   │   │   ├── ENEVA_05_04_2022.xlsx
│   │   │   │   ├── ENEVA_29.05.2024.xlsx
│   │   │   │   ├── ENEVA_29.05.2024__1.xlsx
│   │   │   │   ├── ENEX_17_06_2021.xlsx
│   │   │   │   ├── ENGIE 01072025.xlsx
│   │   │   │   ├── ENGIE COM (GRUPO)_06_10_2021.xlsx
│   │   │   │   ├── ENGIE TRADING_(GRUPO)_18_10_2021.xlsx
│   │   │   │   ├── ENGIE_06.06.2024.xlsx
│   │   │   │   ├── Engie_31082023.xlsx
│   │   │   │   ├── ENGIECOM_06.06.2024.xlsx
│   │   │   │   ├── EngieTrading_05092023.xlsx
│   │   │   │   ├── EQUATORIAL (ECHO)_25092025.xlsx
│   │   │   │   ├── ESFERA 02_08_2022.xlsx
│   │   │   │   ├── ESFERA 26 04 2024.xlsx
│   │   │   │   ├── ESFERA 27022024.xlsx
│   │   │   │   ├── EVEREST 06_05_2022.xlsx
│   │   │   │   ├── EVEREST_03_09_2021.xlsx
│   │   │   │   ├── EVO 20112023.xlsx
│   │   │   │   ├── EVO ENERGIA 27062025.xlsx
│   │   │   │   ├── EVO ENERGIA 30_05_2022.xlsx
│   │   │   │   ├── EVO ENERGIA _25_05_2021.xlsx
│   │   │   │   ├── EVO_20.05.2024.xlsx
│   │   │   │   ├── EVOLUTION_19_03_2021.xlsx
│   │   │   │   ├── EXATA_03_09_2021.xlsx
│   │   │   │   ├── EXPONENCIAL 01112024.xlsx
│   │   │   │   ├── EXPONENCIAL 10_03_2022.xlsx
│   │   │   │   ├── Fibra Energy 14052025.xlsx
│   │   │   │   ├── FICHA AMERICA_18.06.2023.xlsx
│   │   │   │   ├── FICHA ARGON_16.06.2023.xlsx
│   │   │   │   ├── FICHA BOVEN_16.06.2023.xlsx
│   │   │   │   ├── FICHA EXPONENCIAL_16.06.2023.xlsx
│   │   │   │   ├── FICHA GOLD_19.06.2023.xlsx
│   │   │   │   ├── FICHA MODELO_xx.xx.2024.xlsx
│   │   │   │   ├── FICHA MODELO_xx.xx.xxxx.xlsx
│   │   │   │   ├── FICHA MODELO_xx.xx.xxxx__4.xlsx
│   │   │   │   ├── FICHA URCA_20.06.2023.xlsx
│   │   │   │   ├── FLASH 11072025.xlsx
│   │   │   │   ├── FLASH ENERGY 25042024.xlsx
│   │   │   │   ├── FLOW_03_09_2021.xlsx
│   │   │   │   ├── FOCUS ENERGIA _07_05_2021.xlsx
│   │   │   │   ├── FOTOVO 01_09_2022.xlsx
│   │   │   │   ├── FOTOVO_11.08.2023_.xlsx
│   │   │   │   ├── FOTOVO_21.05.2024.xlsx
│   │   │   │   ├── FOZ DO CHAPECO RATING 27012026.xlsx
│   │   │   │   ├── GALP 11122023.xlsx
│   │   │   │   ├── GALP 25112024.xlsx
│   │   │   │   ├── GALP 27082025.xlsx
│   │   │   │   ├── GALP ENERGIA 10_11_2022.xlsx
│   │   │   │   ├── GAMA_06_09_2021.xlsx
│   │   │   │   ├── GENCO 23042024.xlsx
│   │   │   │   ├── GENCO_04042023.xlsx
│   │   │   │   ├── Genco_22_05_2025.xlsx
│   │   │   │   ├── GENIAL 12_04_2022.xlsx
│   │   │   │   ├── Genial 20052025.xlsx
│   │   │   │   ├── GENIAL 27102023.xlsx
│   │   │   │   ├── GENIAL_06_09_2021.xlsx
│   │   │   │   ├── GENIAL_17.05.2024.xlsx
│   │   │   │   ├── GERAMAMORE 27082025.xlsx
│   │   │   │   ├── GERAMAMORE_06.06.2024.xlsx
│   │   │   │   ├── GERAMAMORÉ 30112023.xlsx
│   │   │   │   ├── GERAMAMORÉ_28_10_2021.xlsx
│   │   │   │   ├── GERDAU AÇOS LONGOS 23 04 2024.xlsx
│   │   │   │   ├── Gerdau Aços Longos_20_09_2021.xlsx
│   │   │   │   ├── GET_06_09_2021.xlsx
│   │   │   │   ├── GO ENERGY 25_05_2022.xlsx
│   │   │   │   ├── GO ENERGY 29_11_2021.xlsx
│   │   │   │   ├── GOLD 07_04_2022.xlsx
│   │   │   │   ├── GOLD 27032024 - Copia.xlsx
│   │   │   │   ├── GOLD _05_05_2021.xlsx
│   │   │   │   ├── GRID ENERGIA 04092025.xlsx
│   │   │   │   ├── Grupo BC_19052023.xlsx
│   │   │   │   ├── HUMAITA 09062025.xlsx
│   │   │   │   ├── HYDRO Energia 27022024.xlsx
│   │   │   │   ├── HYDRO ENERGIA_2024.xlsx
│   │   │   │   ├── HYDROENERGIA_19.06.2024.xlsx
│   │   │   │   ├── IBITU 05122024 - Copia.xlsx
│   │   │   │   ├── IBITU 06_06_2022.xlsx
│   │   │   │   ├── IBITU RATING 11112025.xlsx
│   │   │   │   ├── IBS 13_06_2022.xlsx
│   │   │   │   ├── IBS Energy_04082023.xlsx
│   │   │   │   ├── IBS_09_09_2021.xlsx
│   │   │   │   ├── IBS_24_06_2024.xlsx
│   │   │   │   ├── IDEAL 25_05_2022 TESTE.xlsx
│   │   │   │   ├── IDEAL_09_09_2021.xlsx
│   │   │   │   ├── IFT COM 27112023.xlsx
│   │   │   │   ├── IFT_09_09_2021.xlsx
│   │   │   │   ├── INDRA 15_06_2022.xlsx
│   │   │   │   ├── INDRA 16072025.xlsx
│   │   │   │   ├── INDRA_09_09_2021.xlsx
│   │   │   │   ├── INDRA_11042024.xlsx
│   │   │   │   ├── INFINITY 08_08_2022.xlsx
│   │   │   │   ├── INFINITY ENERGIAS 29_11_2021.xlsx
│   │   │   │   ├── Infinity_17.08.2023.xlsx
│   │   │   │   ├── INFINITY_20.05.2024 v2.xlsx
│   │   │   │   ├── ITAU 13062023.xlsx
│   │   │   │   ├── ITAU 30102025.xlsx
│   │   │   │   ├── ITAU COM 02_05_2022.xlsx
│   │   │   │   ├── ITAU_05.07.2024.xlsx
│   │   │   │   ├── J&F 15092025.xlsx
│   │   │   │   ├── J&F DF 2024 holding.xlsx
│   │   │   │   ├── J&F RATING 06112025.xlsx
│   │   │   │   ├── JANDAÍRA I ENERGIAS RENOVÁVEIS S.A._23.07.2024.xlsx
│   │   │   │   ├── JANDAÍRA II ENERGIAS RENOVÁVEIS S.A._23.07.2024.xlsx
│   │   │   │   ├── JANDAÍRA III ENERGIAS RENOVÁVEIS S.A._23.07.2024.xlsx
│   │   │   │   ├── JANDAÍRA IV ENERGIAS RENOVÁVEIS S.A._23.07.2024.xlsx
│   │   │   │   ├── JBS_08.07.2024.xlsx
│   │   │   │   ├── KROMA 17112023.xlsx
│   │   │   │   ├── KROMA 31_05_2022.xlsx
│   │   │   │   ├── KROMA_24_05_2021.xlsx
│   │   │   │   ├── LIBHERTA 01_06_2022.xlsx
│   │   │   │   ├── LIBRA 29 04 2024.xlsx
│   │   │   │   ├── LIBRA 30_05_2022.xlsx
│   │   │   │   ├── LIBRA COMERCIALIZADORA 01102025.xlsx
│   │   │   │   ├── LIBRA_09_09_2021.xlsx
│   │   │   │   ├── LIGHT 18 04 2024.xlsx
│   │   │   │   ├── LIGHT COM  RATING 22122025.xlsx
│   │   │   │   ├── LIGHT_(GRUPO)_18_10_2021.xlsx
│   │   │   │   ├── LIGHT_10_09_2021.xlsx
│   │   │   │   ├── LIVEN COM 17092025.xlsx
│   │   │   │   ├── LOG 27112023.xlsx
│   │   │   │   ├── LOG ENERGIA 01_06_2022.xlsx
│   │   │   │   ├── LOG ENERGIA 29092025.xlsx
│   │   │   │   ├── LOG_10_09_2021.xlsx
│   │   │   │   ├── LOG_17.05.2024.xlsx
│   │   │   │   ├── LOTUS_13.06.2024.xlsx
│   │   │   │   ├── LUDFOR 08052025.xlsx
│   │   │   │   ├── LUDFOR_09_09_2021.xlsx
│   │   │   │   ├── LUDFOR_19062023.xlsx
│   │   │   │   ├── LUDFOR_20.05.2024.xlsx
│   │   │   │   ├── LUX 01_06_2022.xlsx
│   │   │   │   ├── LUX 21052025.xlsx
│   │   │   │   ├── LÉROS_10_09_2021.xlsx
│   │   │   │   ├── MASSARI_13.06.2024.xlsx
│   │   │   │   ├── Matrix -grupo- 03042025(Recuperado Automaticamente).xlsx
│   │   │   │   ├── MATRIX 26_05_2022.xlsx
│   │   │   │   ├── Matrix Grupo 1 11032024.xlsx
│   │   │   │   ├── MATRIX_18_06_2021.xlsx
│   │   │   │   ├── MATRIX_19.06.2024.xlsx
│   │   │   │   ├── MAXIMA 01_02_2023.xlsx
│   │   │   │   ├── Maxima 21112023.xlsx
│   │   │   │   ├── MAXIMA_18_06_2021.xlsx
│   │   │   │   ├── MAXIMA_21.05.2024.xlsx
│   │   │   │   ├── MEGA 04_07_2022.xlsx
│   │   │   │   ├── MEGA WATT_26_10_2021.xlsx
│   │   │   │   ├── MEGA_12052023.xlsx
│   │   │   │   ├── MEGA_16_09_2021.xlsx
│   │   │   │   ├── MEGA_20.06.2024.xlsx
│   │   │   │   ├── MENDUBIM GERAÇÃO 19112024.xlsx
│   │   │   │   ├── MERCATTO COM RATING 14012026.xlsx
│   │   │   │   ├── MERCATTOCOM_13.05.2024.xlsx
│   │   │   │   ├── MERCATTOENERGIA_13.05.2024.xlsx
│   │   │   │   ├── MERCURIO_13.05.2024.xlsx
│   │   │   │   ├── MERITO 14_11_2022.xlsx
│   │   │   │   ├── MERITO_18_06_2021.xlsx
│   │   │   │   ├── MEZ 12122023.xlsx
│   │   │   │   ├── MIGRATIO 02072025.xlsx
│   │   │   │   ├── MIGRATIO 02_06_2022.xlsx
│   │   │   │   ├── Migratio_07062023.xlsx
│   │   │   │   ├── MIGRATIO_17_06_2021.xlsx
│   │   │   │   ├── MINERVA 02_06_2022.xlsx
│   │   │   │   ├── MINERVA 05_06_2025.xlsx
│   │   │   │   ├── MINERVA 25 04 2024.xlsx
│   │   │   │   ├── Minerva_12062023.xlsx
│   │   │   │   ├── NC ENERGIA 21_06_2022.xlsx
│   │   │   │   ├── NC_30.07.2024.xlsx
│   │   │   │   ├── NEO ENERGIA 01102025.xlsx
│   │   │   │   ├── Neoenergia 25082023.xlsx
│   │   │   │   ├── NEW COM 02_08_2022.xlsx
│   │   │   │   ├── NEWAVE 15042024.xlsx
│   │   │   │   ├── NEWAVE 27032026.xlsx
│   │   │   │   ├── NEWAVE_2024.xlsx
│   │   │   │   ├── NEWCOM RATING 27012026.xlsx
│   │   │   │   ├── NEWCOM_09102024.xlsx
│   │   │   │   ├── NEWCOM_19072023.xlsx
│   │   │   │   ├── NEWEN_09_09_2021.xlsx
│   │   │   │   ├── NOVA 25 04 2024.xlsx
│   │   │   │   ├── NOVA ENERGIA 08_06_2022.xlsx
│   │   │   │   ├── Nova Energia_16_06_2021.xlsx
│   │   │   │   ├── NOVA_ENERGIA2024.xlsx
│   │   │   │   ├── OLYMPE 1311223.xlsx
│   │   │   │   ├── OLYMPE 24042024.xlsx
│   │   │   │   ├── OLYMPE 26_10_2022.xlsx
│   │   │   │   ├── OMEGA 13_07_2022.xlsx
│   │   │   │   ├── OMG_07062023.xlsx
│   │   │   │   ├── PACIFICO 18032024.xlsx
│   │   │   │   ├── PACIFICO_10062023.xlsx
│   │   │   │   ├── PACTO 25 04 2024.xlsx
│   │   │   │   ├── PACTO_11.08.2023.xlsx
│   │   │   │   ├── PACTO_2024.xlsx
│   │   │   │   ├── PANENERGY 05042024.xlsx
│   │   │   │   ├── PARATY 02_06_2022.xlsx
│   │   │   │   ├── Paraty 28062024.xlsx
│   │   │   │   ├── PARATY ENERGIA 01102025.xlsx
│   │   │   │   ├── Paraty Energia_30052023.xlsx
│   │   │   │   ├── PARATY_05.07.2024.xlsx
│   │   │   │   ├── PBEN_12.06.2024.xlsx
│   │   │   │   ├── PCH MOINHO  RATING 26012026.xlsx
│   │   │   │   ├── PETRA 09_03_ 2022.xlsx
│   │   │   │   ├── PETRA_06_05_2021( modelo novo).xlsx
│   │   │   │   ├── PETROBRAS PIE 03062025.xlsx
│   │   │   │   ├── PIE RP 17_11_2022.xlsx
│   │   │   │   ├── PLURAL ENERGIA 20_07_2022.xlsx
│   │   │   │   ├── PONTOON 10072025.xlsx
│   │   │   │   ├── PONTOON_29_08_2024.xlsx
│   │   │   │   ├── POWER COM 02_05_2022.xlsx
│   │   │   │   ├── POWER COM 14_06_2022.xlsx
│   │   │   │   ├── PRIME ENERGY 02_06_2022.xlsx
│   │   │   │   ├── PRIME ENERGY 02_08_2022.xlsx
│   │   │   │   ├── PRIME ENERGY _21_06_2021.xlsx
│   │   │   │   ├── PRIME_12.07.2024.xlsx
│   │   │   │   ├── PRIME_16.06.2023.xlsx
│   │   │   │   ├── PWR ENERGIA_15_06_2021.xlsx
│   │   │   │   ├── QAIR 01042026.xlsx
│   │   │   │   ├── QAIR BRASIL (iniciante)_10_10_22.xlsx
│   │   │   │   ├── QAIR_13.06.2024.xlsx
│   │   │   │   ├── RAHCROL_10_09_2021.xlsx
│   │   │   │   ├── RBE 01072025.xlsx
│   │   │   │   ├── RBE 15_06_2022.xlsx
│   │   │   │   ├── RBE 31102023.xlsx
│   │   │   │   ├── RBE_05.06.2024.xlsx
│   │   │   │   ├── RENOVA 26082025.xlsx
│   │   │   │   ├── RIO ENERGY (GRUPO) 23_08_2022.xlsx
│   │   │   │   ├── RIO ENERGY 17_11_2021.xlsx
│   │   │   │   ├── Rio Energy_28032023.xlsx
│   │   │   │   ├── RZK 10112023.xlsx
│   │   │   │   ├── RZK_16.05.2024.xlsx
│   │   │   │   ├── RZK_26_10_2021.xlsx
│   │   │   │   ├── SAFIRA 08_06_2022.xlsx
│   │   │   │   ├── SAFIRA 11042024.xlsx
│   │   │   │   ├── SAFIRA ADM.xlsx
│   │   │   │   ├── SAFIRA COM_05_03_2021.xlsx
│   │   │   │   ├── SAFIRA VAREJISTA_2023.xlsx
│   │   │   │   ├── SAFIRA VAREJISTA_2024.xlsx
│   │   │   │   ├── SAFIRA_12_05_2022.xlsx
│   │   │   │   ├── SAFIRA_27042023.xlsx
│   │   │   │   ├── SAFRA 10072025.xlsx
│   │   │   │   ├── SANTA MARIA_09_09_2021.xlsx
│   │   │   │   ├── SANTA MARIA_16.05.2024.xlsx
│   │   │   │   ├── SANTA MARIA_2024.xlsx
│   │   │   │   ├── SANTADER_26.06.2024.xlsx
│   │   │   │   ├── Santander 13062023.xlsx
│   │   │   │   ├── SANTANDER RATING 24102025.xlsx
│   │   │   │   ├── SEB 16102024.xlsx
│   │   │   │   ├── SEB 16102024__1.xlsx
│   │   │   │   ├── SEB RATING 17112025.xlsx
│   │   │   │   ├── Semper_2024.xlsx
│   │   │   │   ├── SERENA 15072025.xlsx
│   │   │   │   ├── SERENA 18 04 2024.xlsx
│   │   │   │   ├── SGS BRASIL 10_03_2022.xlsx
│   │   │   │   ├── SGS Brasil 19-01-2023.xlsx
│   │   │   │   ├── SHELL ENERGY 08_08_2022.xlsx
│   │   │   │   ├── SIMPLE 06_06_2022.xlsx
│   │   │   │   ├── SIMPLE 27032024.xlsx
│   │   │   │   ├── SIMPLE _14_06_2021.xlsx
│   │   │   │   ├── SIMPLE_2024.xlsx
│   │   │   │   ├── SIMPLE_22032023.xlsx
│   │   │   │   ├── SKOPOS 08_08_2022.xlsx
│   │   │   │   ├── SKOPOS 24 04 2024.xlsx
│   │   │   │   ├── SKOPOS 26082025.xlsx
│   │   │   │   ├── SKOPOS_09_09_2021.xlsx
│   │   │   │   ├── SKOPOS_14072023.xlsx
│   │   │   │   ├── SOL SERRA DO MEL III SPE S.A_20.05.2024.xlsx
│   │   │   │   ├── SOL SERRA DO MEL IV SPE S.A_20.05.2024.xlsx
│   │   │   │   ├── SOL SERRA DO MEL V SPE S.A_20.05.2024.xlsx
│   │   │   │   ├── SOL SERRA DO MEL VI SPE S.A_20.05.2024.xlsx
│   │   │   │   ├── SOLENERGIAS 06_06_2022.xlsx
│   │   │   │   ├── SOLENERGIAS_05.06.2024.xlsx
│   │   │   │   ├── SPIC BRASIL 01_12_2022.xlsx
│   │   │   │   ├── SPIC BRASIL C 13112024.xlsx
│   │   │   │   ├── SPIC COM 27062025.xlsx
│   │   │   │   ├── SPOT_12.06.2024.xlsx
│   │   │   │   ├── SQUADRA 16_11_2022.xlsx
│   │   │   │   ├── SQUADRA_18 04 2024.xlsx
│   │   │   │   ├── Squadra_2024.xlsx
│   │   │   │   ├── SQUADRA_29032023.xlsx
│   │   │   │   ├── STAKRAFT_05.07.2024.xlsx
│   │   │   │   ├── STATKRAFT 24_06_2022.xlsx
│   │   │   │   ├── STATKRAFT 27082025.xlsx
│   │   │   │   ├── STATKRAFT INVESTIMENTOS 29092025.xlsx
│   │   │   │   ├── STATKRAFT_29052023.xlsx
│   │   │   │   ├── STIMA 06_06_2022.xlsx
│   │   │   │   ├── STIMA 11042024.xlsx
│   │   │   │   ├── STIMA_10_09_2021.xlsx
│   │   │   │   ├── Stima_2024.xlsx
│   │   │   │   ├── STIMA_30052023.xlsx
│   │   │   │   ├── SUDOESTE ENERGIA 14_06_2022.xlsx
│   │   │   │   ├── SUZANO 13122023.xlsx
│   │   │   │   ├── SUZANO_04.07.2024.xlsx
│   │   │   │   ├── TAKODA_13.06.2024.xlsx
│   │   │   │   ├── TCCOM_18032024.xlsx
│   │   │   │   ├── TEMPO 08_08_2022.xlsx
│   │   │   │   ├── TEMPO 20112023.xlsx
│   │   │   │   ├── Tempo Energia_10_06_2021.xlsx
│   │   │   │   ├── TEMPO_21.05.2024.xlsx
│   │   │   │   ├── TESLA 06_06_2022.xlsx
│   │   │   │   ├── THERA 08_08_2022.xlsx
│   │   │   │   ├── THERA 30102025.xlsx
│   │   │   │   ├── THERA_04.06.2024.xlsx
│   │   │   │   ├── THERA_08_06_2021.xlsx
│   │   │   │   ├── THERA_10102023.xlsx
│   │   │   │   ├── THOPEN 09072025.xlsx
│   │   │   │   ├── TRADENER 17052024.xlsx
│   │   │   │   ├── TRADENER 29_08_2022.xlsx
│   │   │   │   ├── TRADENER_02_09_2021.xlsx
│   │   │   │   ├── TRADENER_10042025.xlsx
│   │   │   │   ├── Tradener_15092023 - Copia.xlsx
│   │   │   │   ├── TRIA 22052025.xlsx
│   │   │   │   ├── TRIA_03.06.2024.xlsx
│   │   │   │   ├── TRINITY 06_06_2022.xlsx
│   │   │   │   ├── TRINITY ENERGIA_09_06_2021.xlsx
│   │   │   │   ├── TRINITY_09062023.xlsx
│   │   │   │   ├── TRINITY_16.05.2024 v2.xlsx
│   │   │   │   ├── TRUE 22-05-2025.xlsx
│   │   │   │   ├── TRUE 22_03_2022.xlsx
│   │   │   │   ├── TRUE 29 04 2024.xlsx
│   │   │   │   ├── TRUE _06_05_2021.xlsx
│   │   │   │   ├── TRUE_31032023.xlsx
│   │   │   │   ├── TYR 16072025.xlsx
│   │   │   │   ├── ULTRAGAZ 12122025.xlsx
│   │   │   │   ├── URCA 08_08_2022.xlsx
│   │   │   │   ├── URCA 11 04 2024.xlsx
│   │   │   │   ├── URCA_09_09_2021.xlsx
│   │   │   │   ├── VIBRA ENERGIA RATING 06112025.xlsx
│   │   │   │   ├── Vitol 04062025.xlsx
│   │   │   │   ├── VITOL 30 04 2024.xlsx
│   │   │   │   ├── Vitol Power Brasil.xlsx
│   │   │   │   ├── VIVAZ ENERGIA 15_06_2022.xlsx
│   │   │   │   ├── VIX 17_11_2021.xlsx
│   │   │   │   ├── VOLTALIA (GRUPO) 24_08_2022.xlsx
│   │   │   │   ├── VOLTALIA RATING 06112025.xlsx
│   │   │   │   ├── VOTENER (GRUPO)_14_10_2021.xlsx
│   │   │   │   ├── VOTENER_09_06_2021.xlsx
│   │   │   │   ├── W7_25_05_2021.xlsx
│   │   │   │   ├── WORLDSE_20.06.2024.xlsx
│   │   │   │   ├── WX ENERGIA(RAIZEN)_04.07.2024.xlsx
│   │   │   │   ├── WX ENERGY_10_09_2021.xlsx
│   │   │   │   ├── WXE - RAÍZEN 25082023.xlsx
│   │   │   │   ├── XP 05092025.xlsx
│   │   │   │   ├── XP COMERCIALIZADORA 14_07_2022.xlsx
│   │   │   │   ├── XP_03112023.xlsx
│   │   │   │   ├── XP_06_09_2021.xlsx
│   │   │   │   ├── ZEST 15042024.xlsx
│   │   │   │   ├── ZEST 27062025.xlsx
│   │   │   │   ├── ZEST _05_05_2021(modelo novo).xlsx
│   │   │   │   ├── ZEST_26_04_2022.xlsx
│   │   │   │   ├── ZETA 18_04_2022.xlsx
│   │   │   │   ├── ZETA Energia_16_06_2021.xlsx
│   │   │   │   └── ZETA_17032023.xlsx
│   │   │   ├── processadas
│   │   │   ├── rejeitadas
│   │   │   └── reprocessamento
│   │   │       ├── pendentes
│   │   │       ├── processados
│   │   │       │   ├── ATMO 27032026.xlsx
│   │   │       │   ├── BEP ENERGIA RATING 24032026.xlsx
│   │   │       │   ├── CANADIAN RATING 21012026.xlsx
│   │   │       │   ├── CAPITALE 27032026.xlsx
│   │   │       │   ├── CZARNIKOW 27032026.xlsx
│   │   │       │   ├── DANSKE 27032026.xlsx
│   │   │       │   ├── ECOM 27032026.xlsx
│   │   │       │   ├── LIBRA COMERCIALIZADORA 27032026.xlsx
│   │   │       │   ├── SAFIRA 27032026 DF 2024.xlsx
│   │   │       │   ├── SKOPOS 27032026 df 2024.xlsx
│   │   │       │   ├── TRIA 27032026 df 2024.xlsx
│   │   │       │   ├── Vitol 27032026 df 2025.xlsx
│   │   │       │   └── VOLTALIA RATING 06112025.xlsx
│   │   │       └── rejeitados
│   │   │           ├── GERDAU SA RATING 12122025.xlsx
│   │   │           └── QAIR BRASIL RATING 09012026.xlsx
│   │   ├── consumidores
│   │   │   ├── pendentes
│   │   │   │   ├── 3R PETROLEUM  22042024.xlsx
│   │   │   │   ├── 3R PETROLEUM 13082025.xlsx
│   │   │   │   ├── A 100 ROW Serviços de Dados 10082023.xlsx
│   │   │   │   ├── ACO CEARENSE RATING 07012026.xlsx
│   │   │   │   ├── AEBES HEJSN 01122023.xlsx
│   │   │   │   ├── AEGEA 17072025.xlsx
│   │   │   │   ├── AEGEA 20-07-2022.xlsx
│   │   │   │   ├── AEGEA_RIO4_16122024.xlsx
│   │   │   │   ├── Aeroporto Confins 25032025.xlsx
│   │   │   │   ├── AEROPORTO DE GUARULHOS 28082025.xlsx
│   │   │   │   ├── AEROPORTOS DO NORDESTE_16032023.xlsx
│   │   │   │   ├── AGRONORTE RATING 02032026.xlsx
│   │   │   │   ├── AGROPÉU 18062025.xlsx
│   │   │   │   ├── ALBRAS 27052025.xlsx
│   │   │   │   ├── ALCOA ALUMINIO 30052025.xlsx
│   │   │   │   ├── ALCOA ALUMINIO RATING 01122025.xlsx
│   │   │   │   ├── ALIANSCE SONAE_29062023.xlsx
│   │   │   │   ├── ALIANÇA GERAÇÃO 17072025.xlsx
│   │   │   │   ├── ALLIANCE RATING 04022025.xlsx
│   │   │   │   ├── ALUNORTE RATING 18122025.xlsx
│   │   │   │   ├── AMELPLAST RATING 29012026.xlsx
│   │   │   │   ├── Anglo Amercia 27022024 v2.xlsx
│   │   │   │   ├── Anglo Amercia 27022024.xlsx
│   │   │   │   ├── ANGLO AMERICAN 31.12.2023.xlsx
│   │   │   │   ├── ANGLO AMERICAN RATING 14102025.xlsx
│   │   │   │   ├── ARAUCO - 27032025.xlsx
│   │   │   │   ├── ARCELORMITTAL - 00350481.xlsx
│   │   │   │   ├── ARCELORMITTAL RATING 05112025.xlsx
│   │   │   │   ├── Ardagh Metal 26_09_2022.xlsx
│   │   │   │   ├── ARLANXEO_21032023.xlsx
│   │   │   │   ├── ASCENTY 09072025.xlsx
│   │   │   │   ├── ASSAI ATACADISTA 25.07.2024.xlsx
│   │   │   │   ├── ASSAI RATING 09032026.xlsx
│   │   │   │   ├── Assaí atacadista 25032025.xlsx
│   │   │   │   ├── Assaí Atacadista_24072023.xlsx
│   │   │   │   ├── Associação do Hospital de Jaragiuá - Avaliação Middle.xlsx
│   │   │   │   ├── Associação Hospitalar Santana - Avaliação Middle.xlsx
│   │   │   │   ├── ATVOS BIOENERGIA BRENCO RATING 22122025.xlsx
│   │   │   │   ├── ATVOS BIOENERGIA CONQUISTA DO PONTAL RATING 23122025.xlsx
│   │   │   │   ├── ATVOS BIOENERGIA ELDORADO RATING 22122025.xlsx
│   │   │   │   ├── ATVOS BIOENERGIA RIO CLARO RATING 23122025.xlsx
│   │   │   │   ├── ATVOS BIOENERGIA SANTA LUZIA.xlsx
│   │   │   │   ├── AURORA 10082023.xlsx
│   │   │   │   ├── AUTODROMO ENERGÉTICA 13062025.xlsx
│   │   │   │   ├── AVENORTE_20092023.xlsx
│   │   │   │   ├── AVENORTE_30062023.xlsx
│   │   │   │   ├── BALL_02032023.xlsx
│   │   │   │   ├── BASF 25082025.xlsx
│   │   │   │   ├── BE8 RATING 11122025.xlsx
│   │   │   │   ├── BE8_26_08_2024.xlsx
│   │   │   │   ├── BELLO_01062023.xlsx
│   │   │   │   ├── BERNECK 03072025.xlsx
│   │   │   │   ├── Bimbo_02_09_2024.xlsx
│   │   │   │   ├── Bioagri Laboratórios_03-10-2022.xlsx
│   │   │   │   ├── BIOENERGIA BARRA_30062023.xlsx
│   │   │   │   ├── BO Paper 04_05_2022.xlsx
│   │   │   │   ├── BO PAPER RATING 13102025.xlsx
│   │   │   │   ├── BOA FÉ ENERGÉTICA 12062025.xlsx
│   │   │   │   ├── BOPAPER_2023_05_11.xlsx
│   │   │   │   ├── BOZEL BRASIL 21082025.xlsx
│   │   │   │   ├── BRACELL CELULOSE 04082025.xlsx
│   │   │   │   ├── BRADESCO_21_02_2022.xlsx
│   │   │   │   ├── Brasil Tropical 13072023.xlsx
│   │   │   │   ├── BRASKEM - 05 04 2024.xlsx
│   │   │   │   ├── BRASKEM 22072025.xlsx
│   │   │   │   ├── Brasken 01022024 sem eprotocolo.xlsx
│   │   │   │   ├── Brastex - Avaliação Middle.xlsx
│   │   │   │   ├── Brastex 10062024.xlsx
│   │   │   │   ├── BRASTEX RATING 08012026.xlsx
│   │   │   │   ├── Braswell.xlsx
│   │   │   │   ├── BRAVOX_31072023.xlsx
│   │   │   │   ├── BRF 12082024.xlsx
│   │   │   │   ├── BRF FOODS 22072025.xlsx
│   │   │   │   ├── BRF RATING 01122025.xlsx
│   │   │   │   ├── Bridgestone do Brasil.xlsx
│   │   │   │   ├── Bridgestone_24_08_2022 - 2.xlsx
│   │   │   │   ├── Bridgestone_24_08_2022 - 3.xlsx
│   │   │   │   ├── Bridgestone_24_08_2022 - 4.xlsx
│   │   │   │   ├── BRK Ambiental - Avaliação Middle.xlsx
│   │   │   │   ├── C. VALE RATING 07112025.xlsx
│   │   │   │   ├── CAERN_23042025.xlsx
│   │   │   │   ├── CAESB RATING 20012026.xlsx
│   │   │   │   ├── CANOINHAS 17072025.xlsx
│   │   │   │   ├── Caramuru 2022-07-18.xlsx
│   │   │   │   ├── Cargil 05.08.2024.xlsx
│   │   │   │   ├── Cargil 28022024.xlsx
│   │   │   │   ├── CARGILL 15072025.xlsx
│   │   │   │   ├── CBA - Cia Brasileira de Alumínio 2022-07-12.xlsx
│   │   │   │   ├── CEDAE_23082023.xlsx
│   │   │   │   ├── CEEE RATING 02122025.xlsx
│   │   │   │   ├── CEEE-G_02_06_2025.xlsx
│   │   │   │   ├── CEESAM 11-12-2025.xlsx
│   │   │   │   ├── Centrais Eólicas de Caetité Participações S.A. 21012026.xlsx
│   │   │   │   ├── CENTRAL PACK 24082023.xlsx
│   │   │   │   ├── CEPASA 08072025.xlsx
│   │   │   │   ├── Ceramica_Formigres_18_01_2022.xlsx
│   │   │   │   ├── CERÂMICA ELISABETH.xlsx
│   │   │   │   ├── Cessão Flexoprint para All4Labels.xlsx
│   │   │   │   ├── CIA Sulamericana de Distribuição sem eprotocolo.xlsx
│   │   │   │   ├── Cimento Campeão Alvorada_14_01_2022.xlsx
│   │   │   │   ├── CIMENTO ITAMBE 27_07_2022.xlsx
│   │   │   │   ├── CISER 11092025.xlsx
│   │   │   │   ├── CITROSUCO_10042025.xlsx
│   │   │   │   ├── CJ do Brasil_13042023.xlsx
│   │   │   │   ├── COAMO 02062025.xlsx
│   │   │   │   ├── COAMO 11012024.xlsx
│   │   │   │   ├── COASUL RATING 31102025.xlsx
│   │   │   │   ├── Coca-cola FEMSA 05032024.xlsx
│   │   │   │   ├── Cocamar 01022024 sem eprotocolo.xlsx
│   │   │   │   ├── COCAMAR 11012024.xlsx
│   │   │   │   ├── Cocamar 28022024.xlsx
│   │   │   │   ├── COLGATE 24042025.xlsx
│   │   │   │   ├── Companhia Aguas de Joinville - Avaliação Middle.xlsx
│   │   │   │   ├── COMPANHIA DE CIMENTO CAMPEAO ALVORADA RATING 31122025.xlsx
│   │   │   │   ├── COMPANHIA RIOGRANDENSE DE SANEAMENTO 18082025.xlsx
│   │   │   │   ├── COMUSA 05072024.xlsx
│   │   │   │   ├── Continental Camaçari_21_02_2022.xlsx
│   │   │   │   ├── CONTINENTAL_15072024.xlsx
│   │   │   │   ├── CONTINENTAL_15072024_V1.xlsx
│   │   │   │   ├── COOPAVEL 11012024.xlsx
│   │   │   │   ├── Cooper Barras 29_09_2022.xlsx
│   │   │   │   ├── COOPERALIANCA 11012024.xlsx
│   │   │   │   ├── COOPERALIANÇA 01102024.xlsx
│   │   │   │   ├── Cooperativa AGRARIA 28032024.xlsx
│   │   │   │   ├── COPACOL 18082023.xlsx
│   │   │   │   ├── COPACOL_25_08_2022 - 1.xlsx
│   │   │   │   ├── COPACOL_25_08_2022 - 2.xlsx
│   │   │   │   ├── COPAPA RATING 17112025.xlsx
│   │   │   │   ├── COPAVEL RATING 11112025.xlsx
│   │   │   │   ├── Corteva 15_08_2022.xlsx
│   │   │   │   ├── Costa e Palu 16_08_2022.xlsx
│   │   │   │   ├── CP KELKO RATING 02022026.xlsx
│   │   │   │   ├── CPIC 02_02_2023.xlsx
│   │   │   │   ├── CPTM 21072025.xlsx
│   │   │   │   ├── CRELUZ_09102024.xlsx
│   │   │   │   ├── CRIUVA ENERGETICA 12062025.xlsx
│   │   │   │   ├── CSN 04062025.xlsx
│   │   │   │   ├── CSN 31-07-224.xlsx
│   │   │   │   ├── CSN CIMENTOS 08072025.xlsx
│   │   │   │   ├── CSN MINERAÇÃO 22082025.xlsx
│   │   │   │   ├── CVALE_09032023.xlsx
│   │   │   │   ├── DAE SA AGUA E ESGOTO 18082023.xlsx
│   │   │   │   ├── Delta Indústria Cerâmica 28022025.xlsx
│   │   │   │   ├── DEXCO - 15.07.2024.xlsx
│   │   │   │   ├── DEXCO 14072025.xlsx
│   │   │   │   ├── DEXCO S.A._30-06-2022.xlsx
│   │   │   │   ├── DEXCO_28032023.xlsx
│   │   │   │   ├── Diagnósticos da América 08042025.xlsx
│   │   │   │   ├── DIP FRANGOS - 21072025.xlsx
│   │   │   │   ├── Dois Marcos Sementes 03042024.xlsx
│   │   │   │   ├── DOW BRASIL RATING 21012026.xlsx
│   │   │   │   ├── Dulce Acqua_28_09_2022.xlsx
│   │   │   │   ├── DUPLAS RATING 09022026.xlsx
│   │   │   │   ├── EATON_23_02_2022.xlsx
│   │   │   │   ├── EDF 24072025 v2.xlsx
│   │   │   │   ├── EDF VERDECOM RATING 17102025.xlsx
│   │   │   │   ├── ELEKEIROZ 15052024.xlsx
│   │   │   │   ├── ELEKEIROZ_15_08_2024.xlsx
│   │   │   │   ├── Eletrobras_30052025.xlsx
│   │   │   │   ├── Elizabeth Porcelanato.xlsx
│   │   │   │   ├── EMBASA 14042025.xlsx
│   │   │   │   ├── EMBRAER_10042023.xlsx
│   │   │   │   ├── Engetech 10032025.xlsx
│   │   │   │   ├── EPASA 21122023.xlsx
│   │   │   │   ├── ESTADO DE SP 15_08_2022.xlsx
│   │   │   │   ├── ETERNIT RATING 18122025.xlsx
│   │   │   │   ├── EUCATEX RATING 28102025.xlsx
│   │   │   │   ├── EUROFARMA_03102023.xlsx
│   │   │   │   ├── EVONIK 04112024.xlsx
│   │   │   │   ├── EVONIK 13082025.xlsx
│   │   │   │   ├── EVONIK_16062023.xlsx
│   │   │   │   ├── EVONIK_FILIAL 04112024.xlsx
│   │   │   │   ├── EXTRAMIX - Avaliação Middle.xlsx
│   │   │   │   ├── FACCHINI SA 22122025.xlsx
│   │   │   │   ├── FACCHINI_20022025.xlsx
│   │   │   │   ├── FACULDADES ALFA RATING 29102025.xlsx
│   │   │   │   ├── FCA Fiat-Chrysler_22_08_2022.xlsx
│   │   │   │   ├── FERBASA 00355224.xlsx
│   │   │   │   ├── FERNANDEZ INDUSTRIA DE PAPEL RATING 09032026.xlsx
│   │   │   │   ├── Fiação São Bento 08_11_2022.xlsx
│   │   │   │   ├── FIBRAPLAC_12_08_2024.xlsx
│   │   │   │   ├── ficha ARAUCO 2022.xlsx
│   │   │   │   ├── ficha BASF 2022.xlsx
│   │   │   │   ├── ficha FERBASA 2022.xlsx
│   │   │   │   ├── FICHA MODELO ddmmaaaa.xlsx
│   │   │   │   ├── ficha modelo livres acima de 2MWm.xlsx
│   │   │   │   ├── ficha SANTHER 2022-10.xlsx
│   │   │   │   ├── ficha São Eutiquiano Participações (Grupo Maringá) 2022.xlsx
│   │   │   │   ├── ficha Yara Brasil Fertilizantes SA 2022.xlsx
│   │   │   │   ├── Fontain 05032024.xlsx
│   │   │   │   ├── FOSNOR 20-02-225.xlsx
│   │   │   │   ├── Frigoestrela_02052023.xlsx
│   │   │   │   ├── FRIGOESTRELA_20_08_2024.xlsx
│   │   │   │   ├── FRIMESA - 08 04 2024.xlsx
│   │   │   │   ├── FRISIA_03102023.xlsx
│   │   │   │   ├── GAB 10012024.xlsx
│   │   │   │   ├── GAZIT 05022024.xlsx
│   │   │   │   ├── GERDAU ACOMINAS RATING 11122025.xlsx
│   │   │   │   ├── GERDAU Açominas 11122024.xlsx
│   │   │   │   ├── GERDAU Aços Longos 11122024.xlsx
│   │   │   │   ├── GERDAU AÇOS LONGOS 13062025.xlsx
│   │   │   │   ├── GERDAU SA - 13062025.xlsx
│   │   │   │   ├── GERDAU SA 11122024.xlsx
│   │   │   │   ├── GERDAU_23062023.xlsx
│   │   │   │   ├── Globalpack 17012024.xlsx
│   │   │   │   ├── GM do Brasil - Avaliação Middle.xlsx
│   │   │   │   ├── GM RATING 16012026.xlsx
│   │   │   │   ├── Goodyear 2022-07-12.xlsx
│   │   │   │   ├── GPA RATING 07112025.xlsx
│   │   │   │   ├── Grendene 2022-07-28.xlsx
│   │   │   │   ├── Grupo Barigui 05_09_2022.xlsx
│   │   │   │   ├── Grupo GAZIT 10012024.xlsx
│   │   │   │   ├── GRUPO LIDER RATING 11122025.xlsx
│   │   │   │   ├── GRUPO MATHEUS RATING 10032026.xlsx
│   │   │   │   ├── Grupo NC - Avaliação Middle.xlsx
│   │   │   │   ├── Grupo Pão de Açucar 19032024.xlsx
│   │   │   │   ├── Grupo Rocha 23082023.xlsx
│   │   │   │   ├── Grupo São Camilo 16_09_2022.xlsx
│   │   │   │   ├── Grupo Vertical 30082023.xlsx
│   │   │   │   ├── GTFOODS 00354264.xlsx
│   │   │   │   ├── GTOP RATING 12122025.xlsx
│   │   │   │   ├── GUERRO 08042024.xlsx
│   │   │   │   ├── GWEST RATING 03022026.xlsx
│   │   │   │   ├── HAVAN - 08082025.xlsx
│   │   │   │   ├── Heinz Brasil - Avaliação Middle.xlsx
│   │   │   │   ├── HEINZ_20032023.xlsx
│   │   │   │   ├── HEJSN_19_10_2022.xlsx
│   │   │   │   ├── HF SISTEMAS DE FREIOS RATING 26012026.xlsx
│   │   │   │   ├── Hospital Cruz Vermelha - Avaliação Middle.xlsx
│   │   │   │   ├── Hospital Jaraguá 25072023.xlsx
│   │   │   │   ├── Hospital Moinhos de Vento 22_09_2022.xlsx
│   │   │   │   ├── Hospital Pequeno Principe 29_09_2022.xlsx
│   │   │   │   ├── Hospital Policlina Cascavel 2023-01-26.xlsx
│   │   │   │   ├── Hospital São Francisco18_01_23.xlsx
│   │   │   │   ├── HOSPITAL_NOSSA_SENHORA_DAS_DORES_21032023.xlsx
│   │   │   │   ├── HUBNER 19022024.xlsx
│   │   │   │   ├── Hyundai_10082023.xlsx
│   │   │   │   ├── Incepa 20052024.xlsx
│   │   │   │   ├── INDEMIL 27112024.xlsx
│   │   │   │   ├── INDUPA RATING 03112025.xlsx
│   │   │   │   ├── INDUSTRIA VIDREIRA DO NORDESTE RATING 04022026.xlsx
│   │   │   │   ├── INPASA RATING 10122025.xlsx
│   │   │   │   ├── Intercast - Avaliação Middle.xlsx
│   │   │   │   ├── INTERCEMENT - 08072025.xlsx
│   │   │   │   ├── InterCement_20_10_2022.xlsx
│   │   │   │   ├── IRANI_07-07-2022.xlsx
│   │   │   │   ├── Itambe 03042024.xlsx
│   │   │   │   ├── ITAMBE ENERGETICA SA 18082025.xlsx
│   │   │   │   ├── Jacobina Mineração_24_02_2023.xlsx
│   │   │   │   ├── JAGUAFRANGOS 08012024.xlsx
│   │   │   │   ├── Jardim Botânico Participações 28-10-2025.xlsx
│   │   │   │   ├── JBS 11012024.xlsx
│   │   │   │   ├── JBS SA - 08072025.xlsx
│   │   │   │   ├── JBSFILIAL_01102024.xlsx
│   │   │   │   ├── KARSTEN - 15.07.2024.xlsx
│   │   │   │   ├── Karsten 12_09_2022.xlsx
│   │   │   │   ├── Kimberly-Clark análises.xlsx
│   │   │   │   ├── KINROSS 28102025.xlsx
│   │   │   │   ├── Klabin 03112023.xlsx
│   │   │   │   ├── Klabin 12062024.xlsx
│   │   │   │   ├── KLABIN 18_02_2022.xlsx
│   │   │   │   ├── Klabin 26032025.xlsx
│   │   │   │   ├── KORDSA_13032025.xlsx
│   │   │   │   ├── KORDSA_20_04_2022.xlsx
│   │   │   │   ├── KRONA TUBOS e CONEXOES 28042025.xlsx
│   │   │   │   ├── LAR COOPERATIVA 03072025.xlsx
│   │   │   │   ├── LAR COOPERATIVA 07012024 v2.xlsx
│   │   │   │   ├── LDC BRASIL 30062025.xlsx
│   │   │   │   ├── LDC SUCOS 30062025.xlsx
│   │   │   │   ├── LDC TES 30062025.xlsx
│   │   │   │   ├── LIASA 05012024 v2.xlsx
│   │   │   │   ├── LIASA 18062025.xlsx
│   │   │   │   ├── LIASA RATING 24102025.xlsx
│   │   │   │   ├── LIBRA LIGAS - 08 04 2024.xlsx
│   │   │   │   ├── LIBRAS RATING 09032026.xlsx
│   │   │   │   ├── LIGA ALVARO BAHIA RATING 03112025.xlsx
│   │   │   │   ├── LSNC RATING 12122025.xlsx
│   │   │   │   ├── LYCRA_22062023.xlsx
│   │   │   │   ├── LÍDER (Atacadista) 02122024.xlsx
│   │   │   │   ├── M DIAS BRANCO 15082025.xlsx
│   │   │   │   ├── MARFRIG RATING 05112025.xlsx
│   │   │   │   ├── MARINGA FERRO LIGA 26082025.xlsx
│   │   │   │   ├── MESSER GASES 02072025.xlsx
│   │   │   │   ├── Messer Gases 16112023.xlsx
│   │   │   │   ├── MESSER GASES_05052022.xlsx
│   │   │   │   ├── MESSER_27_12_2022.xlsx
│   │   │   │   ├── METAL LEVE - 21082025.xlsx
│   │   │   │   ├── METRO 15072025.xlsx
│   │   │   │   ├── Metro Bahia 18042024.xlsx
│   │   │   │   ├── METRO BAHIA 21082025.xlsx
│   │   │   │   ├── METRO RIO 13082025.xlsx
│   │   │   │   ├── MetroRio_06042023.xlsx
│   │   │   │   ├── Metrô São Paulo_06032023.xlsx
│   │   │   │   ├── MHC PLASTICOS 28072025.xlsx
│   │   │   │   ├── MICHELIN RATING 15012026.xlsx
│   │   │   │   ├── MILI RATING 19112025.xlsx
│   │   │   │   ├── MINERACAO ONCA PUMA RATING 03112025.xlsx
│   │   │   │   ├── Mineração Aurizona 17052024.xlsx
│   │   │   │   ├── MINERAÇÃO AURIZONA 23082023.xlsx
│   │   │   │   ├── MINERAÇÃO PARAGOMINAS - 07082025.xlsx
│   │   │   │   ├── Minerva 01112023.xlsx
│   │   │   │   ├── MINING CORUMBA RATING 28012026.xlsx
│   │   │   │   ├── Moinho Itaipu 29062025.xlsx
│   │   │   │   ├── MOSAIC FERTILIZANTES RATING 21012026.xlsx
│   │   │   │   ├── MOTIVA RATING 25102025.xlsx
│   │   │   │   ├── Muffato 07112023.xlsx
│   │   │   │   ├── NATURAFRIG RATING 20022026.xlsx
│   │   │   │   ├── NEXA 05012026.xlsx
│   │   │   │   ├── NEXA 08072025.xlsx
│   │   │   │   ├── Nitaplast 16_08_2022.xlsx
│   │   │   │   ├── NORFIL 13062025.xlsx
│   │   │   │   ├── NORFIL 15022024.xlsx
│   │   │   │   ├── NORFIL_13_01_23.xlsx
│   │   │   │   ├── NOVO ATACAREJO 28102025.xlsx
│   │   │   │   ├── Oggi Alimentos_13_10_2022.xlsx
│   │   │   │   ├── ORIZON 25092025.xlsx
│   │   │   │   ├── PADO_28062023.xlsx
│   │   │   │   ├── PAPIRUS RATING 25022026.xlsx
│   │   │   │   ├── Paraná Xisto 13012025.xlsx
│   │   │   │   ├── Paraná Xisto 22082023.xlsx
│   │   │   │   ├── PB Gelatinas_03_10_2022.xlsx
│   │   │   │   ├── Peróxidos_24_02_2023.xlsx
│   │   │   │   ├── PETROBRAS RATING 10112025.xlsx
│   │   │   │   ├── PETRORECONCAVO RATING 11112025.xlsx
│   │   │   │   ├── PM Cascavel.xlsx
│   │   │   │   ├── POLIMIX_06062023.xlsx
│   │   │   │   ├── POLO FILMS 20-07-2022.xlsx
│   │   │   │   ├── PORTO ITAPOA RATING 10122025.xlsx
│   │   │   │   ├── PRATI DONADUZZI 24082023.xlsx
│   │   │   │   ├── Prati Donaduzzi_24_06_2022.xlsx
│   │   │   │   ├── PRIMA FOODS RATING 27012026.xlsx
│   │   │   │   ├── PURO PELLET - Avaliação Middle.xlsx
│   │   │   │   ├── QAIR 02072025.xlsx
│   │   │   │   ├── Quimica Amparo YPE - Avaliação Middle.xlsx
│   │   │   │   ├── RAIZEN_20092023.xlsx
│   │   │   │   ├── RANDON 04032024.xlsx
│   │   │   │   ├── Raízen Geo Biogás 13022025.xlsx
│   │   │   │   ├── REDE DOR SÃO LUIZ.xlsx
│   │   │   │   ├── REPINHO 01072025.xlsx
│   │   │   │   ├── REPINHO 29042025.xlsx
│   │   │   │   ├── RIACHUELO_05072023.xlsx
│   │   │   │   ├── RIMA INDSUTRIAL 07072025.xlsx
│   │   │   │   ├── RIMA INDUSTRIAL RATING 04112025.xlsx
│   │   │   │   ├── Rio de Janeiro Refrescos - Avaliação Middle.xlsx
│   │   │   │   ├── Rio de Janeiro Refrescos 16102023.xlsx
│   │   │   │   ├── RIO GALEAO RATING 04112025.xlsx
│   │   │   │   ├── RIO PARANÁ ENERGIA 26112024.xlsx
│   │   │   │   ├── ROMI 16052025.xlsx
│   │   │   │   ├── SABESP RATING 10112025.xlsx
│   │   │   │   ├── SALOBO METAIS 28072025.xlsx
│   │   │   │   ├── SAMARCO 16102023.xlsx
│   │   │   │   ├── SAMARCO RATING 23122025.xlsx
│   │   │   │   ├── SANEAGO_20250106.xlsx
│   │   │   │   ├── SANEPAR 02072025.xlsx
│   │   │   │   ├── SANEPAR 12012024.xlsx
│   │   │   │   ├── SANSUY 10062025 v2.xlsx
│   │   │   │   ├── Santa Maria_11_03_2022.xlsx
│   │   │   │   ├── Santa Terezinha 24032025.xlsx
│   │   │   │   ├── SANTAHELENA_2023_03_15.xlsx
│   │   │   │   ├── Santander 02012024.xlsx
│   │   │   │   ├── Santher 01022024 sem eprotocolo.xlsx
│   │   │   │   ├── Santo Antonio Energia 01102024.xlsx
│   │   │   │   ├── SAO MARTINHO RATING 02022026.xlsx
│   │   │   │   ├── SCALA DATA CENTERS 2025.xlsx
│   │   │   │   ├── Segalas Alimentos - Avaliação Middle.xlsx
│   │   │   │   ├── SENDAS DISTRIBUIDORA 22_08_2022.xlsx
│   │   │   │   ├── SERLONAS RATING 10032026.xlsx
│   │   │   │   ├── SERRANA 11062025.xlsx
│   │   │   │   ├── SERVENG CIVILSAN RATING 12112025.xlsx
│   │   │   │   ├── SLC_AGRICOLA_23_11_2022.xlsx
│   │   │   │   ├── SOFTYS BRASIL 25062025.xlsx
│   │   │   │   ├── SOFTYS_09_03_2022.xlsx
│   │   │   │   ├── SOLAR BEBIDAS SA RATING 09012026.xlsx
│   │   │   │   ├── SOLAR BR ENERGIA RATING 09012026.xlsx
│   │   │   │   ├── SOLAR ENERGIAS RATING 12122025.xlsx
│   │   │   │   ├── SOUTH32 RATING 09122025.xlsx
│   │   │   │   ├── SOUZA CRUZ RATING 04032026.xlsx
│   │   │   │   ├── spal 05032024.xlsx
│   │   │   │   ├── Sta Casa Rio Claro 17102023.xlsx
│   │   │   │   ├── Stara - Avaliação Middle.xlsx
│   │   │   │   ├── SUDATI 08042024.xlsx
│   │   │   │   ├── Sumitomo_10082023.xlsx
│   │   │   │   ├── SUPERMERCADO LIS RATING 29012026.xlsx
│   │   │   │   ├── Supremo Cimentos_02032023.xlsx
│   │   │   │   ├── Suzano 01022024 sem eprotocolo.xlsx
│   │   │   │   ├── SUZANO RATING 03122025.xlsx
│   │   │   │   ├── SUZANO_2023_07_03.xlsx
│   │   │   │   ├── SYLVAMO_20_07_2022.xlsx
│   │   │   │   ├── SÃO PAULO ENERGÉTICA 11062025.xlsx
│   │   │   │   ├── TCP 04082025.xlsx
│   │   │   │   ├── TCP RATING 04112025.xlsx
│   │   │   │   ├── TCP_Paranaguá_16_01_2023.xlsx
│   │   │   │   ├── TECPAR 03072024.xlsx
│   │   │   │   ├── TEREOS AMIDOS E ADOCANTES RATING 27112025.xlsx
│   │   │   │   ├── Termomecânica São Paulo_05102023.xlsx
│   │   │   │   ├── TERNIUM BRASIL 02072025.xlsx
│   │   │   │   ├── Terphane - Avaliação Middle.xlsx
│   │   │   │   ├── TERPHANE RATING 30012026.xlsx
│   │   │   │   ├── TIGRE_27032023.xlsx
│   │   │   │   ├── TIM - Avaliação Middle.xlsx
│   │   │   │   ├── TODIMO_06122024.xlsx
│   │   │   │   ├── TRANSPETRO 09072025.xlsx
│   │   │   │   ├── TRANSVIDA RATING 20022026.xlsx
│   │   │   │   ├── TRENS DE SP 21082025.xlsx
│   │   │   │   ├── TROMBINI - 15.07.2024.xlsx
│   │   │   │   ├── TROMBINI 28082023.xlsx
│   │   │   │   ├── Trombini_10_11_2022.xlsx
│   │   │   │   ├── TUPY 14072025.xlsx
│   │   │   │   ├── TUPY_15052023.xlsx
│   │   │   │   ├── UNIGEL - Proquigel 30-01-2023.xlsx
│   │   │   │   ├── UNIGEL 24072025.xlsx
│   │   │   │   ├── Unilever_17112023.xlsx
│   │   │   │   ├── UNIPAR RATING 04112025.xlsx
│   │   │   │   ├── UNIRON_10_10_2022.xlsx
│   │   │   │   ├── União Química 14112023.xlsx
│   │   │   │   ├── USIMINAS 07072025.xlsx
│   │   │   │   ├── V.TAL RATING 31102025.xlsx
│   │   │   │   ├── VALE 30-05-2025.xlsx
│   │   │   │   ├── VALGROUP PACKAGING SOLUTIONS - Avaliação Middle.xlsx
│   │   │   │   ├── VALLOUREC SOLUCOES RATING 08012026.xlsx
│   │   │   │   ├── VALLOUREC TUBOS RATING 08012025.xlsx
│   │   │   │   ├── VEOLIA_28082024.xlsx
│   │   │   │   ├── VERALLIA_02_12_2022.xlsx
│   │   │   │   ├── VIBRA 26.07.2024.xlsx
│   │   │   │   ├── VIBRA_05092025.xlsx
│   │   │   │   ├── VIDROPORTO RATING 03022026.xlsx
│   │   │   │   ├── VILLARES METALS RATING 12112025.xlsx
│   │   │   │   ├── VILLARES_14032023.xlsx
│   │   │   │   ├── VIPAL_05042023.xlsx
│   │   │   │   ├── VIRACOPOS - 04042024.xlsx
│   │   │   │   ├── Vista Foods 15122023.xlsx
│   │   │   │   ├── Vitopel_2023_07_27.xlsx
│   │   │   │   ├── VIVIX 28_07_2022.xlsx
│   │   │   │   ├── Volks 21-07-2022.xlsx
│   │   │   │   ├── VOLKSWAGEN RATING 08012026.xlsx
│   │   │   │   ├── VOTORANTIM 07072025.xlsx
│   │   │   │   ├── VOTORANTIM NNE 20082025.xlsx
│   │   │   │   ├── Votorantim.xlsx
│   │   │   │   ├── VW do Brasil_18072023.xlsx
│   │   │   │   ├── WEG 03072025.xlsx
│   │   │   │   ├── WEG 11012024.xlsx
│   │   │   │   ├── WEG 25112024.xlsx
│   │   │   │   ├── WHB_08042024.xlsx
│   │   │   │   ├── WHB_11042024.xlsx
│   │   │   │   ├── WHIRLPOOL_24_04_2023.xlsx
│   │   │   │   ├── WHITE MARTINS 20082025.xlsx
│   │   │   │   └── YARA NITROGENADOS RATING 11112025.xlsx
│   │   │   ├── processadas
│   │   │   ├── rejeitadas
│   │   │   └── reprocessamento
│   │   │       ├── pendentes
│   │   │       └── processados
│   │   │           └── GERDAU AÇOS LONGOS RATING 27032026.xlsx
│   │   └── reprocessamento
│   │       └── pendentes
│   ├── garantias
│   │   └── garantias.csv
│   ├── mtm
│   │   └── data.csv
│   ├── receita
│   │   └── cache
│   │       └── receita_cache.json
│   └── salesforce
│       └── salesforce.xlsx
├── LOGS
│   └── runner
├── SAIDAS
│   ├── bronze
│   │   ├── blacklist_raw
│   │   ├── fichas_comercializadoras_raw
│   │   ├── fichas_consumidores_raw
│   │   ├── ingestion_log
│   │   ├── mtm_raw
│   │   ├── receita_raw
│   │   ├── salesforce_raw
│   │   └── snapshots_fontes
│   ├── gold
│   │   ├── alertas_credito
│   │   ├── historico_analises
│   │   ├── pendencias
│   │   ├── relatorio_credito_atual
│   │   └── visao_operacional_negocio
│   ├── output
│   ├── relational
│   │   ├── configs
│   │   ├── control
│   │   │   ├── ctl_campo_origem.parquet
│   │   │   ├── ctl_documento.parquet
│   │   │   ├── ctl_run_pipeline.csv
│   │   │   └── ctl_run_pipeline.parquet
│   │   ├── dimensions
│   │   └── facts
│   ├── silver
│   │   ├── fichas_comercializadoras_extraidas
│   │   └── fichas_consumidores_extraidas
│   └── staging
│       ├── blacklist
│       ├── fichas_comercializadoras
│       ├── fichas_consumidores
│       ├── mtm
│       ├── receita
│       └── salesforce
├── src
│   ├── app
│   │   ├── comercializadoras
│   │   │   └── orquestrador.py
│   │   ├── consumidores
│   │   │   ├── classificacao.py
│   │   │   └── orquestrador.py
│   │   ├── __init__.py
│   │   ├── bootstrap.py
│   │   ├── config_builder.py
│   │   └── context.py
│   ├── cli
│   │   ├── __init__.py
│   │   ├── rodar_fichas_comercializadoras.py
│   │   └── rodar_fichas_consumidores.py
│   ├── common
│   │   ├── __init__.py
│   │   ├── domain_normalizer.py
│   │   ├── excel.py
│   │   ├── hashing.py
│   │   ├── json.py
│   │   ├── paths.py
│   │   ├── servico_desduplicacao.py
│   │   └── validador.py
│   ├── control
│   │   ├── __init__.py
│   │   ├── carregador_de_mapeamento.py
│   │   ├── field_types.py
│   │   ├── layout_catalog.py
│   │   ├── logger.py
│   │   └── quality_loader.py
│   ├── domain
│   │   ├── auditoria
│   │   │   ├── __init__.py
│   │   │   └── servico_auditoria.py
│   │   ├── cadastro
│   │   │   ├── __init__.py
│   │   │   ├── servico_bureau.py
│   │   │   └── servico_receita.py
│   │   ├── carga_manual
│   │   │   ├── __init__.py
│   │   │   └── servico_carga_manual.py
│   │   ├── contrapartes
│   │   │   ├── __init__.py
│   │   │   ├── segmentacao.py
│   │   │   ├── servico_dim_contraparte.py
│   │   │   └── servico_enquadramento.py
│   │   ├── contratos
│   │   │   ├── __init__.py
│   │   │   └── servico_contratos_denodo.py
│   │   ├── credito
│   │   │   ├── __init__.py
│   │   │   ├── ead_engine.py
│   │   │   ├── lgd_engine.py
│   │   │   ├── notas_quantitativas_cpura.py
│   │   │   ├── pd_base.py
│   │   │   ├── pd_cgrupo.py
│   │   │   ├── pd_consumidor_gt5.py
│   │   │   ├── pd_consumidor_le5.py
│   │   │   ├── pd_cpura.py
│   │   │   ├── pd_exceptions.py
│   │   │   ├── pd_motor.py
│   │   │   ├── pd_transform.py
│   │   │   ├── pd_validator.py
│   │   │   ├── pe_engine.py
│   │   │   ├── rating.py
│   │   │   ├── score_qualitativo.py
│   │   │   ├── score_quantitativo.py
│   │   │   ├── score_total.py
│   │   │   ├── servico_fato_analise_credito.py
│   │   │   ├── servico_override.py
│   │   │   ├── servico_risco.py
│   │   │   └── taxa_risco_engine.py
│   │   ├── fichas
│   │   │   ├── __init__.py
│   │   │   ├── classificador.py
│   │   │   ├── derivador_financeiro.py
│   │   │   ├── extrator.py
│   │   │   ├── ficha_extractor.py
│   │   │   └── validador.py
│   │   ├── garantias
│   │   │   ├── __init__.py
│   │   │   ├── garantia_model.py
│   │   │   └── servico_garantia.py
│   │   ├── mtm
│   │   │   ├── __init__.py
│   │   │   ├── servico_denodo_mtm_reconciliacao.py
│   │   │   └── servico_mtm.py
│   │   ├── salesforce
│   │   │   ├── __init__.py
│   │   │   ├── servico_salesforce.py
│   │   │   └── servico_salesforce_reconciliacao.py
│   │   ├── __init__.py
│   │   └── enums.py
│   ├── gold
│   │   ├── __init__.py
│   │   └── service_gold.py
│   ├── relational
│   │   └── __init__.py
│   ├── services
│   │   ├── connectors
│   │   │   ├── __init__.py
│   │   │   ├── denodo_connector.py
│   │   │   ├── mtm_connector.py
│   │   │   ├── receita_connector.py
│   │   │   ├── risk3_connector.py
│   │   │   └── salesforce_connector.py
│   │   └── __init__.py
│   ├── silver
│   │   ├── __init__.py
│   │   ├── documentos_classificados.py
│   │   ├── normalizador_de_tipo_de_campo.py
│   │   └── normalizadores.py
│   ├── staging
│   │   ├── __init__.py
│   │   ├── descoberta.py
│   │   └── staging_arquivo.py
│   └── storage
│       ├── __init__.py
│       ├── armazenamento_manifest.py
│       ├── bronze_arquivo.py
│       ├── escrever_dados.py
│       ├── estado_armazenamento.py
│       └── operacao_arquivo.py
├── .env
├── .gitignore
├── 0_obter_e_triar.py
├── app_dashboard.py
├── gerar_contexto_ia.py
├── main.py
└── reset.py