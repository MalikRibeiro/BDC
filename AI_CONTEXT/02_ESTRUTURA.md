# ESTRUTURA

BDC/
├── .agents/
│   ├── rules/
│   │   └── bd-credito-rules.md
│   └── workflows/
│       └── bd-credito-workflow.md
├── docs/
│   ├── architecture_data_contracts.md
│   ├── auditoria_silver_comercializadoras.md
│   ├── implementation_plan.md
│   ├── planejamento_sistema_bd_credito_operacional_v1_2.pdf
│   ├── prompt_auditoria_bdc.md
│   └── relatorio_auditoria_final.md
├── ENTRADAS/
│   ├── atualizacoes_manuais/
│   │   ├── diagnostico/
│   │   │   └── fila_pendencias.csv
│   │   ├── pendentes/
│   │   ├── processadas/
│   │   ├── rejeitadas/
│   │   └── carga_manual_assistida_20260902_174236.xlsx
│   ├── blacklist/
│   ├── bureau/
│   │   └── cache/
│   │       └── risk3_cache.json
│   ├── configs/
│   │   ├── app_config.json
│   │   └── config.json
│   ├── contratos_denodo/
│   │   └── com-query-1788206919826.csv
│   ├── control/
│   │   ├── configs/
│   │   │   ├── pd_cpura_config.json
│   │   │   ├── pd_faixas.json
│   │   │   ├── pd_transform_rules.json
│   │   │   └── score_cpura_config.json
│   │   ├── layouts/
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
│   │   ├── mappings/
│   │   │   ├── mapping_fichas_comercializadoras.json
│   │   │   └── mapping_fichas_consumidores.json
│   │   ├── quality/
│   │   │   ├── data_quality_rules_fichas_consumidores.json
│   │   │   ├── domain_dictionaries.json
│   │   │   ├── master_catalog_comercializadoras.json
│   │   │   ├── master_catalog_consumidores.json
│   │   │   └── pk_fk_rules.json
│   │   └── schemas/
│   │       ├── schema_app_config.json
│   │       ├── schema_carga_manual.json
│   │       ├── schema_config.json
│   │       ├── schema_data_quality_rules.json
│   │       ├── schema_ficha_comercializadora_extraida.json
│   │       ├── schema_ficha_consumidor_extraida.json
│   │       ├── schema_ingestion_log.json
│   │       ├── schema_mapping_fichas_comercializadoras.json
│   │       └── schema_mapping_fichas_consumidores.json
│   ├── fichas/
│   │   ├── comercializadoras/
│   │   │   ├── pendentes/
│   │   │   ├── processadas/
│   │   │   │   ├── 2W ENERGIA 05_07_2022.xlsx
│   │   │   │   ├── 2W ENERGIA_28.08.2024.xlsx
│   │   │   │   ├── 2W_13062023 - Copia.xlsx
│   │   │   │   ├── 2W_18_06_2021.xlsx
│   │   │   │   ├── ABC 14072026.xlsx
│   │   │   │   ├── ABC 29.07.2024.xlsx
│   │   │   │   ├── ABC BRASIL 15102025.xlsx
│   │   │   │   ├── ADN 02062026.xlsx
│   │   │   │   ├── AES_05012024.xlsx
│   │   │   │   ├── AES_19.06.2024.xlsx
│   │   │   │   ├── AGE COMERCIALIZADORA 30062026.xlsx
│   │   │   │   ├── AGORA ENERGIA 09062026.xlsx
│   │   │   │   ├── AGORA21.05.2024.xlsx
│   │   │   │   ├── AGROENERGIA _10_05_2021.xlsx
│   │   │   │   ├── ALBIOMA 09072026.xlsx
│   │   │   │   ├── ALBIOMA CODORA.xlsx
│   │   │   │   ├── ALCAST_12.07.2024.xlsx
│   │   │   │   ├── ALIANCA_GERACAO 28052026.xlsx
│   │   │   │   ├── ALIANÇA 20_07_2022.xlsx
│   │   │   │   ├── ALIANÇA GERAÇÃO RATING 06022026.xlsx
│   │   │   │   ├── ALUPAR 19112024.xlsx
│   │   │   │   ├── ALUPAR_06062025.xlsx
│   │   │   │   ├── AMAGGI 11_07_2022.xlsx
│   │   │   │   ├── AMAGGI RATING 05022026.xlsx
│   │   │   │   ├── AMBAR 11122023.xlsx
│   │   │   │   ├── AMBAR 26_04_2022.xlsx
│   │   │   │   ├── AMBAR_29.07.2024.xlsx
│   │   │   │   ├── AMBAR_31_08_2021.xlsx
│   │   │   │   ├── AMERICA_07_06_2021.xlsx
│   │   │   │   ├── AMERICA_20.05.2024.xlsx
│   │   │   │   ├── ANGELIM 09062026.xlsx
│   │   │   │   ├── ANGELINA COLOMBO 29072026.xlsx
│   │   │   │   ├── ANGELINA COLOMBO.xlsx
│   │   │   │   ├── APOLLO 08 05 2024.xlsx
│   │   │   │   ├── APOLO 02_05_2022.xlsx
│   │   │   │   ├── APOLO_24_06_2021.xlsx
│   │   │   │   ├── AQUARIUS 11062026.xlsx
│   │   │   │   ├── ARCELORMITTAL_21.05.2024.xlsx
│   │   │   │   ├── ARMOR 15082025.xlsx
│   │   │   │   ├── ARMOR_20.05.2024.xlsx
│   │   │   │   ├── ARMOS_07062023.xlsx
│   │   │   │   ├── ASOLO 29052026.xlsx
│   │   │   │   ├── ATHENA 29_08_2022.xlsx
│   │   │   │   ├── ATIAIA 18082026.xlsx
│   │   │   │   ├── ATIAIA 24062025.xlsx
│   │   │   │   ├── ATIAIA RATING 06022026.xlsx
│   │   │   │   ├── ATLAS_18022025.xlsx
│   │   │   │   ├── ATMO 04052026.xlsx
│   │   │   │   ├── ATMO 06_05_2022.xlsx
│   │   │   │   ├── ATMO 16052025.xlsx
│   │   │   │   ├── ATMO 16052025__1.xlsx
│   │   │   │   ├── ATMO 27032026.xlsx
│   │   │   │   ├── ATMO_06.06.2024.xlsx
│   │   │   │   ├── ATMO_16062023.xlsx
│   │   │   │   ├── ATMO_31_08_2021.xlsx
│   │   │   │   ├── ATVOS BRENCO 27072026.xlsx
│   │   │   │   ├── ATVOS PART. 03082026.xlsx
│   │   │   │   ├── ATVOS RIO CLARO 31072026.xlsx
│   │   │   │   ├── AUREN COM 22072026.xlsx
│   │   │   │   ├── AUREN_13.06.2024.xlsx
│   │   │   │   ├── AUREN_16062023.xlsx
│   │   │   │   ├── AUREN_24092025.xlsx
│   │   │   │   ├── AXIA 24082026.xlsx
│   │   │   │   ├── B2R 27_06_2022.xlsx
│   │   │   │   ├── B2R ENERGIA_20122021.xlsx
│   │   │   │   ├── B2R_06.06.2024.xlsx
│   │   │   │   ├── B2R_22.05.2024.xlsx
│   │   │   │   ├── Banco ABC 05092023.xlsx
│   │   │   │   ├── BARIGUI_17.05.2024.xlsx
│   │   │   │   ├── BARIGUI_17032023.xlsx
│   │   │   │   ├── BARRALCOOL 13072026.xlsx
│   │   │   │   ├── BC 06_05_2022.xlsx
│   │   │   │   ├── BC COMERCIALIZADORA 27032026.xlsx
│   │   │   │   ├── BC_05042024.xlsx
│   │   │   │   ├── BEM 10062026.xlsx
│   │   │   │   ├── BEP 08_06_2022.xlsx
│   │   │   │   ├── BEP 09072025 - Copia.xlsx
│   │   │   │   ├── BEP 31_08_2021.xlsx
│   │   │   │   ├── BEP ENERGIA RATING 24032026.xlsx
│   │   │   │   ├── BEP_16.05.2024.xlsx
│   │   │   │   ├── BEVAP 11082026.xlsx
│   │   │   │   ├── BEVAP SA RATING 03032026.xlsx
│   │   │   │   ├── BID ENERGY 04_05_2022.xlsx
│   │   │   │   ├── BID_12.06.2024.xlsx
│   │   │   │   ├── BID_13102023.xlsx
│   │   │   │   ├── BIOENERGETICA BOA VISTA RATING 03022026.xlsx
│   │   │   │   ├── BIOENERGETICA SANTA CRUZ RATING 02022026.xlsx
│   │   │   │   ├── BIOENERGÉTICA SÃO MARTINHO RATING 02022026.xlsx
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
│   │   │   │   ├── BRADESCO 30072026.xlsx
│   │   │   │   ├── BRASIL COM 11_07_2022.xlsx
│   │   │   │   ├── BRASIL COM_11_06_2021.xlsx
│   │   │   │   ├── BRASIL COM_18_04_2023.xlsx
│   │   │   │   ├── BRASIL SERVICOS_08_06_2021.xlsx
│   │   │   │   ├── BRASIL Serviços_18042023.xlsx
│   │   │   │   ├── BRASKEN 19 04 2024.xlsx
│   │   │   │   ├── BRAVO 08052026.xlsx
│   │   │   │   ├── BRAVO 11042024.xlsx
│   │   │   │   ├── Bravo_2024 (Salvo automaticamente).xlsx
│   │   │   │   ├── BRAVO_25_10_2021.xlsx
│   │   │   │   ├── BRAVO_26052023.xlsx
│   │   │   │   ├── BRF Energia 15072025.xlsx
│   │   │   │   ├── BROOKFIELD_01_09_2021.xlsx
│   │   │   │   ├── BROOKFILD 04_05_2022.xlsx
│   │   │   │   ├── BTG 01102024.xlsx
│   │   │   │   ├── BTG 15102025.xlsx
│   │   │   │   ├── BTG_05092023.xlsx
│   │   │   │   ├── BTG_29.07.2024.xlsx
│   │   │   │   ├── CANADIAN 08062026.xlsx
│   │   │   │   ├── CANADIAN RATING 21012026.xlsx
│   │   │   │   ├── CAPITALE 01102025.xlsx
│   │   │   │   ├── CAPITALE 27032026.xlsx
│   │   │   │   ├── CAPITALE 28052026.xlsx
│   │   │   │   ├── CAPITALE 30_05_2022.xlsx
│   │   │   │   ├── CAPITALE_16062023.xlsx
│   │   │   │   ├── CAPITALE_26.06.2024.xlsx
│   │   │   │   ├── CASA DOS VENTOS 03 05 2024.xlsx
│   │   │   │   ├── CASA DOS VENTOS 08_06_2022.xlsx
│   │   │   │   ├── CASA DOS VENTOS 30072026.xlsx
│   │   │   │   ├── CASA DOS VENTOS RATING 29102025.xlsx
│   │   │   │   ├── CASA_DOS_VENTOS_11082023.xlsx
│   │   │   │   ├── CASTROLANDA 01042024.xlsx
│   │   │   │   ├── CASTROLANDA 10122025.xlsx
│   │   │   │   ├── CEEE 14042026.xlsx
│   │   │   │   ├── CEI 10092025.xlsx
│   │   │   │   ├── CEI COMERCIALIZADORA 17082026.xlsx
│   │   │   │   ├── CEI ENERGETICA 17082026.xlsx
│   │   │   │   ├── CELESC 11_05_2022.xlsx
│   │   │   │   ├── CELESC Geração 28052026.xlsx
│   │   │   │   ├── CELESC_16042024.xlsx
│   │   │   │   ├── CEMIG 05-07-2024 trading.xlsx
│   │   │   │   ├── CEMIG_09062023.xlsx
│   │   │   │   ├── CEMIG_13.06.2024.xlsx
│   │   │   │   ├── CEMIG_24092025.xlsx
│   │   │   │   ├── CENTRAL 06_05_2022.xlsx
│   │   │   │   ├── CENTRAL 08 05 2024.xlsx
│   │   │   │   ├── Central_22_05_2025.xlsx
│   │   │   │   ├── CERCAR SA RATING 12022026.xlsx
│   │   │   │   ├── CGN 05122025.xlsx
│   │   │   │   ├── CGN Brasil 11082026.xlsx
│   │   │   │   ├── CGN_30.07.2024.xlsx
│   │   │   │   ├── CGN_30102023.xlsx
│   │   │   │   ├── COMEL 18062025.xlsx
│   │   │   │   ├── COMEL_2023.xlsx
│   │   │   │   ├── COMERC 13_06_2022.xlsx
│   │   │   │   ├── COMERC 29 04 2024.xlsx
│   │   │   │   ├── COMERC PART 23072026.xlsx
│   │   │   │   ├── COMERC Participações 28112023.xlsx
│   │   │   │   ├── COMERC_19062023.xlsx
│   │   │   │   ├── CONVEX 18082026.xlsx
│   │   │   │   ├── COPEL_23.07.2024.xlsx
│   │   │   │   ├── COPELCOM_16_04_2021.xlsx
│   │   │   │   ├── COPELGET_27112024.xlsx
│   │   │   │   ├── COPPREL 16062026.xlsx
│   │   │   │   ├── COPREL GERAÇÃO 23062026.xlsx
│   │   │   │   ├── COTESA 30_05_2022.xlsx
│   │   │   │   ├── COTESA_14_10_2021.xlsx
│   │   │   │   ├── CPFL 04072025.xlsx
│   │   │   │   ├── CPFL 04072025__1.xlsx
│   │   │   │   ├── CPFL 06082026.xlsx
│   │   │   │   ├── CPFL_11.08.2023_.xlsx
│   │   │   │   ├── CPFL_28.08.2024.xlsx
│   │   │   │   ├── CTG 24092025.xlsx
│   │   │   │   ├── CTG BRNE_28.08.2024.xlsx
│   │   │   │   ├── CTG NE 02022024.xlsx
│   │   │   │   ├── CTG Trading_04_06_2021.xlsx
│   │   │   │   ├── CTG Trading_16082023.xlsx
│   │   │   │   ├── CTG trading_28.08.2024.xlsx
│   │   │   │   ├── CTGBRNE 10042026.xlsx
│   │   │   │   ├── CTGNE 23072026.xlsx
│   │   │   │   ├── CZARNIKOW 09062026.xlsx
│   │   │   │   ├── CZARNIKOW 13062025.xlsx
│   │   │   │   ├── Czarnikow 27-01-2025.xlsx
│   │   │   │   ├── CZARNIKOW 27032026.xlsx
│   │   │   │   ├── CZARNIKOW 27_09_2022.xlsx
│   │   │   │   ├── CZARNIKOW_07_06_2021 (zerada manualmente).xlsx
│   │   │   │   ├── D3 Comercializadora_18.03.2024.xlsx
│   │   │   │   ├── DANSKE 10072025.xlsx
│   │   │   │   ├── DANSKE 12112024.xlsx
│   │   │   │   ├── DANSKE 27032026.xlsx
│   │   │   │   ├── DANSKE 30072026.xlsx
│   │   │   │   ├── DEAL 10_05_2022.xlsx
│   │   │   │   ├── DEAL 16102025.xlsx
│   │   │   │   ├── DEAL 27102023.xlsx
│   │   │   │   ├── DEAL 29062026.xlsx
│   │   │   │   ├── DEAL RATING 16102025.xlsx
│   │   │   │   ├── DEAL_14_10_2021.xlsx
│   │   │   │   ├── DEAL_26.06.2024.xlsx
│   │   │   │   ├── DELTA 12_04_2022 31 12 2021.xlsx
│   │   │   │   ├── DELTA_19022025.xlsx
│   │   │   │   ├── DESTTRA_02_09_2021.xlsx
│   │   │   │   ├── DIFERENCIAL 13_04_2022.xlsx
│   │   │   │   ├── DIFERENCIAL_02_09_2021.xlsx
│   │   │   │   ├── DIFERENCIAL_16.05.2024.xlsx
│   │   │   │   ├── DIFERENCIAL_20072023.xlsx
│   │   │   │   ├── ECEL - ELETRON_03_09_2021.xlsx
│   │   │   │   ├── ECHOENERGIA 30062026.xlsx
│   │   │   │   ├── Echoenergia Participações.xlsx
│   │   │   │   ├── ECHOENERGIA_09_09_2021.xlsx
│   │   │   │   ├── ECOM 17_05_2022.xlsx
│   │   │   │   ├── ECOM 22042026.xlsx
│   │   │   │   ├── ECOM 23112023.xlsx
│   │   │   │   ├── ECOM 27032026.xlsx
│   │   │   │   ├── ECOM_11042024.xlsx
│   │   │   │   ├── ECOM_14_10_2021.xlsx
│   │   │   │   ├── ECOM_2024.xlsx
│   │   │   │   ├── EDF 01042026.xlsx
│   │   │   │   ├── EDF 06122023.xlsx
│   │   │   │   ├── EDF 30062026.xlsx
│   │   │   │   ├── EDF RENEWABLES VERDECOM 03082026.xlsx
│   │   │   │   ├── EDF VERDECOM 22082025.xlsx
│   │   │   │   ├── EDP 21052026.xlsx
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
│   │   │   │   ├── ELETROBRAS.xlsx
│   │   │   │   ├── ELETROBRAS_24092025.xlsx
│   │   │   │   ├── ELETRON 30_05_2022.xlsx
│   │   │   │   ├── ENECEL_03_09_2021.xlsx
│   │   │   │   ├── ENECEL_26.06.2024.xlsx
│   │   │   │   ├── Enel Brasil_25092025.xlsx
│   │   │   │   ├── ENEL TRADING 27112023.xlsx
│   │   │   │   ├── ENEL_29.07.2024.xlsx
│   │   │   │   ├── ENERCORE 01072026.xlsx
│   │   │   │   ├── ENERCORE 07_04_2022.xlsx
│   │   │   │   ├── ENERCORE_11042024.xlsx
│   │   │   │   ├── ENERCORE_2024.xlsx
│   │   │   │   ├── ENERCORE_22032023.xlsx
│   │   │   │   ├── ENERGEST 17082026.xlsx
│   │   │   │   ├── ENERGETICA 03_03_2022.xlsx
│   │   │   │   ├── ENERGISA 07052024.xlsx
│   │   │   │   ├── ENERGISA 08052026.xlsx
│   │   │   │   ├── ENERGISA 30102025.xlsx
│   │   │   │   ├── ENERGIZOU 17_03_2022.xlsx
│   │   │   │   ├── ENERGIZOU_05.06.2024.xlsx
│   │   │   │   ├── ENERPEIXE 20082026.xlsx
│   │   │   │   ├── ENERPEIXE COMERCIALIZADORA16092025.xlsx
│   │   │   │   ├── ENEVA 28072026.xlsx
│   │   │   │   ├── ENEVA 30102025.xlsx
│   │   │   │   ├── ENEVA_29.05.2024.xlsx
│   │   │   │   ├── ENEVA_29.05.2024__1.xlsx
│   │   │   │   ├── ENEX_17_06_2021.xlsx
│   │   │   │   ├── ENGEFORM 25062026.xlsx
│   │   │   │   ├── ENGIE 01072025.xlsx
│   │   │   │   ├── ENGIE 12052026.xlsx
│   │   │   │   ├── ENGIE_06.06.2024.xlsx
│   │   │   │   ├── Engie_31082023.xlsx
│   │   │   │   ├── ENGIECOM_06.06.2024.xlsx
│   │   │   │   ├── EngieTrading_05092023.xlsx
│   │   │   │   ├── EQUATORIAL (ECHO)_25092025.xlsx
│   │   │   │   ├── EQUATORIAL RENOVAVEIS 08062026.xlsx
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
│   │   │   │   ├── FIBRA 06082026.xlsx
│   │   │   │   ├── Fibra Energy 14052025.xlsx
│   │   │   │   ├── FIBRA_GRUPO 24062025.xlsx
│   │   │   │   ├── FICHA ARGON_16.06.2023.xlsx
│   │   │   │   ├── FICHA BOVEN_16.06.2023.xlsx
│   │   │   │   ├── FICHA EXPONENCIAL_16.06.2023.xlsx
│   │   │   │   ├── FICHA GOLD_19.06.2023.xlsx
│   │   │   │   ├── FICHA MODELO_xx.xx.2024.xlsx
│   │   │   │   ├── FICHA MODELO_xx.xx.2025_1.0.xlsx
│   │   │   │   ├── FICHA MODELO_xx.xx.xxxx.xlsx
│   │   │   │   ├── FICHA MODELO_xx.xx.xxxx__4.xlsx
│   │   │   │   ├── FICHA URCA_20.06.2023.xlsx
│   │   │   │   ├── FICHA_GERADORAS_LAJARI_PASSO4.xlsx
│   │   │   │   ├── FLASH 11072025.xlsx
│   │   │   │   ├── FLASH ENERGY 25042024.xlsx
│   │   │   │   ├── FLOW_03_09_2021.xlsx
│   │   │   │   ├── FOCUS ENERGIA _07_05_2021.xlsx
│   │   │   │   ├── FOTOVO 01_09_2022.xlsx
│   │   │   │   ├── FOTOVO 30-04-2026.xlsx
│   │   │   │   ├── FOTOVO_11.08.2023_.xlsx
│   │   │   │   ├── FOTOVO_21.05.2024.xlsx
│   │   │   │   ├── Foz do Chapeco 05082026.xlsx
│   │   │   │   ├── FOZ DO CHAPECO RATING 27012026.xlsx
│   │   │   │   ├── GALP 11122023.xlsx
│   │   │   │   ├── GALP 25112024.xlsx
│   │   │   │   ├── GALP 27082025.xlsx
│   │   │   │   ├── GALP ENERGIA 10_11_2022.xlsx
│   │   │   │   ├── GAMA_06_09_2021.xlsx
│   │   │   │   ├── GENCO 23042024.xlsx
│   │   │   │   ├── Genco_22_05_2025.xlsx
│   │   │   │   ├── GENIAL 12_04_2022.xlsx
│   │   │   │   ├── Genial 20052025.xlsx
│   │   │   │   ├── GENIAL 27102023.xlsx
│   │   │   │   ├── GENIAL ENERGY 15072026.xlsx
│   │   │   │   ├── GENIAL_06_09_2021.xlsx
│   │   │   │   ├── GENIAL_17.05.2024.xlsx
│   │   │   │   ├── GERAMAMORE 27082025.xlsx
│   │   │   │   ├── GERAMAMORE_06.06.2024.xlsx
│   │   │   │   ├── GERAMAMORÉ 30112023.xlsx
│   │   │   │   ├── GERAMAMORÉ RATING 00359795.xlsx
│   │   │   │   ├── GERAMAMORÉ_28_10_2021.xlsx
│   │   │   │   ├── Gerdau 01042026.xlsx
│   │   │   │   ├── GERDAU AÇOS LONGOS 23 04 2024.xlsx
│   │   │   │   ├── Gerdau Aços Longos_20_09_2021.xlsx
│   │   │   │   ├── GET_06_09_2021.xlsx
│   │   │   │   ├── GO ENERGY 25_05_2022.xlsx
│   │   │   │   ├── GO ENERGY 29_11_2021.xlsx
│   │   │   │   ├── GOLD 07_04_2022.xlsx
│   │   │   │   ├── GOLD 27032024 - Copia.xlsx
│   │   │   │   ├── GOLD _05_05_2021.xlsx
│   │   │   │   ├── GRID ENERGIA 04092025.xlsx
│   │   │   │   ├── GRID ENERGIA 23062026.xlsx
│   │   │   │   ├── HUMAITA 09062025.xlsx
│   │   │   │   ├── HYDRO Energia 27022024.xlsx
│   │   │   │   ├── HYDRO ENERGIA_2024.xlsx
│   │   │   │   ├── HYDROENERGIA_19.06.2024.xlsx
│   │   │   │   ├── IBITU 05122024 - Copia.xlsx
│   │   │   │   ├── IBITU 06_06_2022.xlsx
│   │   │   │   ├── IBITU 19062026.xlsx
│   │   │   │   ├── IBITU RATING 11112025.xlsx
│   │   │   │   ├── IBS 13_06_2022.xlsx
│   │   │   │   ├── IBS Energy_04082023.xlsx
│   │   │   │   ├── IBS_09_09_2021.xlsx
│   │   │   │   ├── IBS_24_06_2024.xlsx
│   │   │   │   ├── IDEAL 25_05_2022 TESTE.xlsx
│   │   │   │   ├── IDEAL_09_09_2021.xlsx
│   │   │   │   ├── IFT 04-05-2026.xlsx
│   │   │   │   ├── IFT COM 27112023.xlsx
│   │   │   │   ├── IFT_09_09_2021.xlsx
│   │   │   │   ├── IJUÍ 02072026.xlsx
│   │   │   │   ├── IJUÍ 13072026.xlsx
│   │   │   │   ├── INDRA 15_06_2022.xlsx
│   │   │   │   ├── INDRA 16072025.xlsx
│   │   │   │   ├── INDRA_09_09_2021.xlsx
│   │   │   │   ├── INDRA_11042024.xlsx
│   │   │   │   ├── INFINITY 04-05-2026.xlsx
│   │   │   │   ├── INFINITY 08_08_2022.xlsx
│   │   │   │   ├── INFINITY ENERGIAS 29_11_2021.xlsx
│   │   │   │   ├── Infinity_17.08.2023.xlsx
│   │   │   │   ├── INFINITY_20.05.2024 v2.xlsx
│   │   │   │   ├── INPASA 05082026.xlsx
│   │   │   │   ├── IPIRA Energia S.A. - 00484431.xlsx
│   │   │   │   ├── ISFIDA RATING 05032026.xlsx
│   │   │   │   ├── ITAMBE ENERGETICA 29072026.xlsx
│   │   │   │   ├── ITAU 13062023.xlsx
│   │   │   │   ├── ITAU 30102025.xlsx
│   │   │   │   ├── ITAU COM 28052026.xlsx
│   │   │   │   ├── ITAU_05.07.2024.xlsx
│   │   │   │   ├── J&F 15092025.xlsx
│   │   │   │   ├── J&F 20082026.xlsx
│   │   │   │   ├── J&F DF 2024 holding.xlsx
│   │   │   │   ├── J&F RATING 06112025.xlsx
│   │   │   │   ├── JANDAÍRA I ENERGIAS RENOVÁVEIS S.A._23.07.2024.xlsx
│   │   │   │   ├── JANDAÍRA II ENERGIAS RENOVÁVEIS S.A._23.07.2024.xlsx
│   │   │   │   ├── JANDAÍRA III ENERGIAS RENOVÁVEIS S.A._23.07.2024.xlsx
│   │   │   │   ├── JANDAÍRA IV ENERGIAS RENOVÁVEIS S.A._23.07.2024.xlsx
│   │   │   │   ├── JARDIM BOTÂNICO GERAÇÃO 06052026.xlsx
│   │   │   │   ├── JBS_08.07.2024.xlsx
│   │   │   │   ├── JSAFRA 15072026.xlsx
│   │   │   │   ├── KROMA 17112023.xlsx
│   │   │   │   ├── KROMA 31_05_2022.xlsx
│   │   │   │   ├── KROMA_24_05_2021.xlsx
│   │   │   │   ├── LAJARI ENERGETICA RATING 26012026.xlsx
│   │   │   │   ├── LIBHERTA 01_06_2022.xlsx
│   │   │   │   ├── LIBRA 05052026.xlsx
│   │   │   │   ├── LIBRA 29 04 2024.xlsx
│   │   │   │   ├── LIBRA 30_05_2022.xlsx
│   │   │   │   ├── LIBRA COMERCIALIZADORA 01102025.xlsx
│   │   │   │   ├── LIBRA COMERCIALIZADORA 27032026.xlsx
│   │   │   │   ├── LIBRA_09_09_2021.xlsx
│   │   │   │   ├── LIBRA_2024.xlsx
│   │   │   │   ├── LIGHT 18 04 2024.xlsx
│   │   │   │   ├── LIGHT COM  RATING 22122025.xlsx
│   │   │   │   ├── LIGHT COM 07052026.xlsx
│   │   │   │   ├── LIGHT_10_09_2021.xlsx
│   │   │   │   ├── LIGHT_2024.xlsx
│   │   │   │   ├── LIVEN 22042026.xlsx
│   │   │   │   ├── LIVEN COM 17092025.xlsx
│   │   │   │   ├── LOG 27112023.xlsx
│   │   │   │   ├── LOG ENERGIA 01_06_2022.xlsx
│   │   │   │   ├── LOG ENERGIA 29092025.xlsx
│   │   │   │   ├── LOG_10_09_2021.xlsx
│   │   │   │   ├── LOG_17.05.2024.xlsx
│   │   │   │   ├── LOTUS_13.06.2024.xlsx
│   │   │   │   ├── LUDFOR 08052025.xlsx
│   │   │   │   ├── LUDFOR 11062026.xlsx
│   │   │   │   ├── LUDFOR COM 08052025.xlsx
│   │   │   │   ├── Ludfor geradora 16072026.xlsx
│   │   │   │   ├── LUDFOR_09_09_2021.xlsx
│   │   │   │   ├── LUDFOR_19062023.xlsx
│   │   │   │   ├── LUDFOR_20.05.2024.xlsx
│   │   │   │   ├── LUX 01_06_2022.xlsx
│   │   │   │   ├── LUX 19082026.xlsx
│   │   │   │   ├── LUX 21052025.xlsx
│   │   │   │   ├── LUX RATING 02032026.xlsx
│   │   │   │   ├── LÉROS_10_09_2021.xlsx
│   │   │   │   ├── MARACANA 06082026.xlsx
│   │   │   │   ├── MARACANÃ ENERGÉTICA RATING 22012026.xlsx
│   │   │   │   ├── MASSARI_13.06.2024.xlsx
│   │   │   │   ├── Matrix -grupo- 03042025(Recuperado Automaticamente).xlsx
│   │   │   │   ├── MATRIX 26_05_2022.xlsx
│   │   │   │   ├── MATRIX COM 17072026.xlsx
│   │   │   │   ├── Matrix Grupo 1 11032024.xlsx
│   │   │   │   ├── MATRIX_18_06_2021.xlsx
│   │   │   │   ├── MATRIX_19.06.2024.xlsx
│   │   │   │   ├── MATRIX_PURA_03042025.xlsx
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
│   │   │   │   ├── MINERVA COM 04082026.xlsx
│   │   │   │   ├── MINERVA RATING.xlsx
│   │   │   │   ├── Minerva_12062023.xlsx
│   │   │   │   ├── NC_30.07.2024.xlsx
│   │   │   │   ├── NEC ENERGIA 06072026.xlsx
│   │   │   │   ├── NEC ENERGIA 18082026.xlsx
│   │   │   │   ├── NEC GERACAO 18082026.xlsx
│   │   │   │   ├── NEO ENERGIA 01102025.xlsx
│   │   │   │   ├── Neoenergia 25082023.xlsx
│   │   │   │   ├── NEOENERGIA RATING 24032026.xlsx
│   │   │   │   ├── NEW COM 02_08_2022.xlsx
│   │   │   │   ├── NEWAVE 15042024.xlsx
│   │   │   │   ├── NEWAVE 27032026.xlsx
│   │   │   │   ├── NEWAVE_2024.xlsx
│   │   │   │   ├── NEWCOM RATING 27012026.xlsx
│   │   │   │   ├── NEWCOM_09102024.xlsx
│   │   │   │   ├── NEWCOM_19072023.xlsx
│   │   │   │   ├── NEWEN_09_09_2021.xlsx
│   │   │   │   ├── NORSK HYDRO 16042026.xlsx
│   │   │   │   ├── NORSK HYDRO ENERGIA 09072026.xlsx
│   │   │   │   ├── NORTE ENERGIA 14052026.xlsx
│   │   │   │   ├── NOVA 25 04 2024.xlsx
│   │   │   │   ├── NOVA ENERGIA 08_06_2022.xlsx
│   │   │   │   ├── Nova Energia_16_06_2021.xlsx
│   │   │   │   ├── NOVA GUAPORE 12082026.xlsx
│   │   │   │   ├── NOVA_ENERGIA2024.xlsx
│   │   │   │   ├── OLYMPE 1311223.xlsx
│   │   │   │   ├── OLYMPE 24042024.xlsx
│   │   │   │   ├── OLYMPE 26_10_2022.xlsx
│   │   │   │   ├── OMG_07062023.xlsx
│   │   │   │   ├── PACIFICO 18032024.xlsx
│   │   │   │   ├── PACIFICO_10062023.xlsx
│   │   │   │   ├── PACTO 25 04 2024.xlsx
│   │   │   │   ├── PACTO_11.08.2023.xlsx
│   │   │   │   ├── PACTO_2024.xlsx
│   │   │   │   ├── PAECOM 29052026.xlsx
│   │   │   │   ├── PANENERGY 05042024.xlsx
│   │   │   │   ├── PARACATU RATING 26022026.xlsx
│   │   │   │   ├── PARATY 02_06_2022.xlsx
│   │   │   │   ├── Paraty 28062024.xlsx
│   │   │   │   ├── PARATY ENERGIA 01102025.xlsx
│   │   │   │   ├── Paraty Energia_30052023.xlsx
│   │   │   │   ├── PARATY_05.07.2024.xlsx
│   │   │   │   ├── PBEN_12.06.2024.xlsx
│   │   │   │   ├── PCH - NOVA GUARPORE RATING.xlsx
│   │   │   │   ├── PCH MOINHO  RATING 26012026.xlsx
│   │   │   │   ├── PETRA 09_03_ 2022.xlsx
│   │   │   │   ├── PETRA_06_05_2021( modelo novo).xlsx
│   │   │   │   ├── PETROBRAS PIE 03062025.xlsx
│   │   │   │   ├── PIE RP 17_11_2022.xlsx
│   │   │   │   ├── PLURAL ENERGIA 20_07_2022.xlsx
│   │   │   │   ├── POLLARIX 03062026.xlsx
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
│   │   │   │   ├── RENOVA 12062026.xlsx
│   │   │   │   ├── RENOVA 26082025.xlsx
│   │   │   │   ├── RENOVA BR RI.xlsx
│   │   │   │   ├── RENOVA COM 27082025.xlsx
│   │   │   │   ├── RIALMA V 06072026.xlsx
│   │   │   │   ├── Rio Canoas (CTG) 17042026.xlsx
│   │   │   │   ├── RIO ENERGY 17_11_2021.xlsx
│   │   │   │   ├── Rio Energy_28032023.xlsx
│   │   │   │   ├── Rio Parana 14042026.xlsx
│   │   │   │   ├── RIO PARANAPANEMA 13042026.xlsx
│   │   │   │   ├── RZK 10112023.xlsx
│   │   │   │   ├── RZK_16.05.2024.xlsx
│   │   │   │   ├── RZK_26_10_2021.xlsx
│   │   │   │   ├── SAFIRA 08_06_2022.xlsx
│   │   │   │   ├── SAFIRA 11042024.xlsx
│   │   │   │   ├── SAFIRA 27032026 DF 2024.xlsx
│   │   │   │   ├── SAFIRA ADM.xlsx
│   │   │   │   ├── SAFIRA COM_05_03_2021.xlsx
│   │   │   │   ├── SAFIRA VAREJISTA_2023.xlsx
│   │   │   │   ├── SAFIRA VAREJISTA_2024.xlsx
│   │   │   │   ├── SAFIRA_12_05_2022.xlsx
│   │   │   │   ├── SAFIRA_27042023.xlsx
│   │   │   │   ├── SAFRA 10072025.xlsx
│   │   │   │   ├── SANTA HELENA ENERGIA 15062026.xlsx
│   │   │   │   ├── SANTA MARIA 11082026.xlsx
│   │   │   │   ├── SANTA MARIA_09_09_2021.xlsx
│   │   │   │   ├── SANTA MARIA_16.05.2024.xlsx
│   │   │   │   ├── SANTA MARIA_2024.xlsx
│   │   │   │   ├── SANTADER_26.06.2024.xlsx
│   │   │   │   ├── Santander 13062023.xlsx
│   │   │   │   ├── SANTANDER RATING 24102025.xlsx
│   │   │   │   ├── SEB 16102024.xlsx
│   │   │   │   ├── SEB 16102024__1.xlsx
│   │   │   │   ├── SEB RATING 17112025.xlsx
│   │   │   │   ├── SEB RATING 2023.xlsx
│   │   │   │   ├── SEMPER 02062026.xlsx
│   │   │   │   ├── Semper_2024.xlsx
│   │   │   │   ├── SERENA 15072025.xlsx
│   │   │   │   ├── SERENA 18 04 2024.xlsx
│   │   │   │   ├── SERRA DAS VACAS HOLDING II.xlsx
│   │   │   │   ├── SGS BRASIL 10_03_2022.xlsx
│   │   │   │   ├── SGS Brasil 19-01-2023.xlsx
│   │   │   │   ├── SHELL 07052026.xlsx
│   │   │   │   ├── SHELL ENERGY 08_08_2022.xlsx
│   │   │   │   ├── SIMPLE 02072026.xlsx
│   │   │   │   ├── SIMPLE 06_06_2022.xlsx
│   │   │   │   ├── SIMPLE 27032024.xlsx
│   │   │   │   ├── SIMPLE _14_06_2021.xlsx
│   │   │   │   ├── SIMPLE_2024.xlsx
│   │   │   │   ├── SKOPOS 02062026.xlsx
│   │   │   │   ├── SKOPOS 08_08_2022.xlsx
│   │   │   │   ├── SKOPOS 24 04 2024.xlsx
│   │   │   │   ├── SKOPOS 26082025.xlsx
│   │   │   │   ├── SKOPOS 27032026 df 2024.xlsx
│   │   │   │   ├── SKOPOS_09_09_2021.xlsx
│   │   │   │   ├── SKOPOS_14072023.xlsx
│   │   │   │   ├── SOL SERRA DO MEL III SPE S.A_20.05.2024.xlsx
│   │   │   │   ├── SOL SERRA DO MEL IV SPE S.A_20.05.2024.xlsx
│   │   │   │   ├── SOL SERRA DO MEL V SPE S.A_20.05.2024.xlsx
│   │   │   │   ├── SOL SERRA DO MEL VI SPE S.A_20.05.2024.xlsx
│   │   │   │   ├── SOLAR ENERGIA RATING COM 13012026.xlsx
│   │   │   │   ├── SOLENERGIAS 06_06_2022.xlsx
│   │   │   │   ├── SOLENERGIAS_05.06.2024.xlsx
│   │   │   │   ├── SPIC 13072026.xlsx
│   │   │   │   ├── SPIC BRASIL C 13112024.xlsx
│   │   │   │   ├── SPIC COM 27062025.xlsx
│   │   │   │   ├── SPOT_12.06.2024.xlsx
│   │   │   │   ├── SQUADRA 16_11_2022.xlsx
│   │   │   │   ├── SQUADRA_18 04 2024.xlsx
│   │   │   │   ├── Squadra_2024.xlsx
│   │   │   │   ├── SQUADRA_29032023.xlsx
│   │   │   │   ├── STAKRAFT_05.07.2024.xlsx
│   │   │   │   ├── STATKRAFT 13082026.xlsx
│   │   │   │   ├── STATKRAFT 27082025.xlsx
│   │   │   │   ├── STATKRAFT INVESTIMENTOS 29092025.xlsx
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
│   │   │   │   ├── THOPEN ENERGIA 20072026.xlsx
│   │   │   │   ├── THOPEN ENERGY RATING 28112025.xlsx
│   │   │   │   ├── TRADENER 17052024.xlsx
│   │   │   │   ├── TRADENER 29_08_2022.xlsx
│   │   │   │   ├── TRADENER_02_09_2021.xlsx
│   │   │   │   ├── TRADENER_10042025.xlsx
│   │   │   │   ├── Tradener_15092023 - Copia.xlsx
│   │   │   │   ├── TRIA 04082026.xlsx
│   │   │   │   ├── TRIA 22052025.xlsx
│   │   │   │   ├── TRIA 27032026 df 2024.xlsx
│   │   │   │   ├── TRIA RATING 28102025.xlsx
│   │   │   │   ├── TRIA_03.06.2024.xlsx
│   │   │   │   ├── TRIEX 26032026.xlsx
│   │   │   │   ├── TRINITY 06_06_2022.xlsx
│   │   │   │   ├── TRINITY ENERGIA_09_06_2021.xlsx
│   │   │   │   ├── TRINITY_16.05.2024 v2.xlsx
│   │   │   │   ├── TRUE 14042026.xlsx
│   │   │   │   ├── TRUE 22-05-2025.xlsx
│   │   │   │   ├── TRUE 22_03_2022.xlsx
│   │   │   │   ├── TRUE 29 04 2024.xlsx
│   │   │   │   ├── TRUE _06_05_2021.xlsx
│   │   │   │   ├── TYR 16072025.xlsx
│   │   │   │   ├── UHE SAO SIMAO 14052026.xlsx
│   │   │   │   ├── ULTRAGAZ 12122025.xlsx
│   │   │   │   ├── ULTRAGAZ 14052026.xlsx
│   │   │   │   ├── URCA 08_08_2022.xlsx
│   │   │   │   ├── URCA 11 04 2024.xlsx
│   │   │   │   ├── URCA_09_09_2021.xlsx
│   │   │   │   ├── URUCUIA 23062026.xlsx
│   │   │   │   ├── USINA MONTE ALEGRE 15072026.xlsx
│   │   │   │   ├── UTE VALE DO PARANA.xlsx
│   │   │   │   ├── VIBRA ENERGIA RATING 06112025.xlsx
│   │   │   │   ├── Vitol 04062025.xlsx
│   │   │   │   ├── VITOL 05062026.xlsx
│   │   │   │   ├── Vitol 27032026 df 2025.xlsx
│   │   │   │   ├── VITOL 30 04 2024.xlsx
│   │   │   │   ├── VITOL POWER 20072026.xlsx
│   │   │   │   ├── Vitol Power Brasil.xlsx
│   │   │   │   ├── VIVAZ ENERGIA 15_06_2022.xlsx
│   │   │   │   ├── VIX 17_11_2021.xlsx
│   │   │   │   ├── VOLTALIA RATING 06112025.xlsx
│   │   │   │   ├── VOLTALIA_2024.xlsx
│   │   │   │   ├── VOTENER_09_06_2021.xlsx
│   │   │   │   ├── W7_25_05_2021.xlsx
│   │   │   │   ├── WD AGROINDUSTRIAL 13072026.xlsx
│   │   │   │   ├── WORLDSE_20.06.2024.xlsx
│   │   │   │   ├── WX ENERGIA(RAIZEN)_04.07.2024.xlsx
│   │   │   │   ├── WX ENERGY_10_09_2021.xlsx
│   │   │   │   ├── WXE - RAÍZEN 25082023.xlsx
│   │   │   │   ├── XP 05092025.xlsx
│   │   │   │   ├── XP 19052025.xlsx
│   │   │   │   ├── XP COM 17072026.xlsx
│   │   │   │   ├── XP COMERCIALIZADORA 14_07_2022.xlsx
│   │   │   │   ├── XP RATING 13112025.xlsx
│   │   │   │   ├── XP_03112023.xlsx
│   │   │   │   ├── XP_06_09_2021.xlsx
│   │   │   │   ├── ZEST 15042024.xlsx
│   │   │   │   ├── ZEST 27062025.xlsx
│   │   │   │   ├── ZEST _05_05_2021(modelo novo).xlsx
│   │   │   │   ├── ZEST_26_04_2022.xlsx
│   │   │   │   ├── ZETA 18_04_2022.xlsx
│   │   │   │   └── ZETA Energia_16_06_2021.xlsx
│   │   │   ├── rejeitadas/
│   │   │   │   ├── AES BRASIL 09_05_2022 TESTE GRUPO.xlsx
│   │   │   │   ├── AMAGGI 26062025.xlsx
│   │   │   │   ├── APTCOM_10052023.xlsx
│   │   │   │   ├── AUREN (VOTENER) 06_05_2022.xlsx
│   │   │   │   ├── BANCO BOCOM BBM 25_05_2022.xlsx
│   │   │   │   ├── BANCO BTG PACTUAL (GRUPO) 14_07_2022.xlsx
│   │   │   │   ├── BEP 09072025.xlsx
│   │   │   │   ├── Bravo_2024.xlsx
│   │   │   │   ├── BTG PACTUAL (BANCO)_08-11_2021.xlsx
│   │   │   │   ├── CANADIAN RARTING 26022026.xlsx
│   │   │   │   ├── CANADIAN SOLAR_06_10_2022.xlsx
│   │   │   │   ├── CANADIAN_17042023.xlsx
│   │   │   │   ├── CDV_SIMULACAO.xlsx
│   │   │   │   ├── CDVSA 12082026.xlsx
│   │   │   │   ├── CEESAM 23072026.xlsx
│   │   │   │   ├── CEMIG H COMERCIALIZAÇÃO_23_02_2022.xlsx
│   │   │   │   ├── CPFL_01_06_2022.xlsx
│   │   │   │   ├── Delta Energia 01072025.xlsx
│   │   │   │   ├── ENEL 22_06_2022.xlsx
│   │   │   │   ├── ENERGISA(GRUPO)_04_09_2021.xlsx
│   │   │   │   ├── ENEVA_05042023.xlsx
│   │   │   │   ├── ENEVA_05_04_2022.xlsx
│   │   │   │   ├── ENGIE COM (GRUPO)_06_10_2021.xlsx
│   │   │   │   ├── ENGIE TRADING_(GRUPO)_18_10_2021.xlsx
│   │   │   │   ├── Fibra_2024.xlsx
│   │   │   │   ├── FICHA AMERICA_18.06.2023.xlsx
│   │   │   │   ├── Ficha Padrão Backup.xlsx
│   │   │   │   ├── Ficha Padrão.xlsx
│   │   │   │   ├── GALAPAGOS 30102025.xlsx
│   │   │   │   ├── GENCO_04042023.xlsx
│   │   │   │   ├── Grupo BC_19052023.xlsx
│   │   │   │   ├── ICAL ENERGIA 16042026.xlsx
│   │   │   │   ├── ITAMBÉ ENERGÉTICA.xlsx
│   │   │   │   ├── ITAU COM 02_05_2022.xlsx
│   │   │   │   ├── J&F 0108025.xlsx
│   │   │   │   ├── LDC 30062025.xlsx
│   │   │   │   ├── LDC BRASIL 29102025.xlsx
│   │   │   │   ├── LIGHT_(GRUPO)_18_10_2021.xlsx
│   │   │   │   ├── Matrix -grupo- 03042025.xlsx
│   │   │   │   ├── NC ENERGIA 21_06_2022.xlsx
│   │   │   │   ├── NOVA - 03042025.xlsx
│   │   │   │   ├── OMEGA 13_07_2022.xlsx
│   │   │   │   ├── Passo_5_Sao_Martinho_Rating_Final.xlsx
│   │   │   │   ├── PCH VERDE 2 ENERGETICA RATING 23012026.xlsx
│   │   │   │   ├── RIO ENERGY (GRUPO) 23_08_2022.xlsx
│   │   │   │   ├── SAFIRA Holding 2023.xlsx
│   │   │   │   ├── SAFIRA Holding.xlsx
│   │   │   │   ├── SIMPLE_22032023.xlsx
│   │   │   │   ├── SPIC BRASIL 01_12_2022.xlsx
│   │   │   │   ├── SPIC BRASIL 07052026.xlsx
│   │   │   │   ├── STATKRAFT 24_06_2022.xlsx
│   │   │   │   ├── STATKRAFT_29052023.xlsx
│   │   │   │   ├── SUZANO_COPILOT.xlsx
│   │   │   │   ├── TEREOS 15072026.xlsx
│   │   │   │   ├── TIMBRO TRADING 15072026.xlsx
│   │   │   │   ├── TRINITY_09062023.xlsx
│   │   │   │   ├── TRUE_31032023.xlsx
│   │   │   │   ├── UHE SAO SIMAO 29082025.xlsx
│   │   │   │   ├── VOLTALIA (GRUPO) 24_08_2022.xlsx
│   │   │   │   ├── VOTENER (GRUPO)_14_10_2021.xlsx
│   │   │   │   └── ZETA_17032023.xlsx
│   │   │   └── reprocessamento/
│   │   │       ├── pendentes/
│   │   │       ├── processadas/
│   │   │       │   ├── ADN 02062026.xlsx
│   │   │       │   ├── AGE COMERCIALIZADORA 30062026.xlsx
│   │   │       │   ├── AGORA ENERGIA 09062026.xlsx
│   │   │       │   ├── ANGELIM 09062026.xlsx
│   │   │       │   ├── ANGELINA COLOMBO 29072026.xlsx
│   │   │       │   ├── AQUARIUS 11062026.xlsx
│   │   │       │   ├── ARCELORMITTAL_21.05.2024.xlsx
│   │   │       │   ├── ASOLO 29052026.xlsx
│   │   │       │   ├── ATMO 04052026.xlsx
│   │   │       │   ├── BEM 10062026.xlsx
│   │   │       │   ├── BEP ENERGIA RATING 24032026.xlsx
│   │   │       │   ├── BRAVO 08052026.xlsx
│   │   │       │   ├── CANADIAN 08062026.xlsx
│   │   │       │   ├── CAPITALE 28052026.xlsx
│   │   │       │   ├── CELESC Geração 28052026.xlsx
│   │   │       │   ├── COPPREL 16062026.xlsx
│   │   │       │   ├── COPREL GERAÇÃO 23062026.xlsx
│   │   │       │   ├── CZARNIKOW 09062026.xlsx
│   │   │       │   ├── DEAL 29062026.xlsx
│   │   │       │   ├── ECOM 22042026.xlsx
│   │   │       │   ├── ELETROBRAS.xlsx
│   │   │       │   ├── ELETROBRAS_24092025.xlsx
│   │   │       │   ├── ENERCORE 01072026.xlsx
│   │   │       │   ├── ENGEFORM 25062026.xlsx
│   │   │       │   ├── Gerdau 01042026.xlsx
│   │   │       │   ├── GRID ENERGIA 23062026.xlsx
│   │   │       │   ├── IJUÍ 13072026.xlsx
│   │   │       │   ├── IPIRA Energia S.A. - 00484431.xlsx
│   │   │       │   ├── JARDIM BOTÂNICO GERAÇÃO 06052026.xlsx
│   │   │       │   ├── LIBRA 05052026.xlsx
│   │   │       │   ├── LIVEN 22042026.xlsx
│   │   │       │   ├── Ludfor geradora 16072026.xlsx
│   │   │       │   ├── NEC GERACAO 18082026.xlsx
│   │   │       │   ├── NORSK HYDRO ENERGIA 09072026.xlsx
│   │   │       │   ├── POLLARIX 03062026.xlsx
│   │   │       │   ├── RENOVA 12062026.xlsx
│   │   │       │   ├── SANTA HELENA ENERGIA 15062026.xlsx
│   │   │       │   ├── SEMPER 02062026.xlsx
│   │   │       │   ├── SERRA DAS VACAS HOLDING II.xlsx
│   │   │       │   ├── SHELL 07052026.xlsx
│   │   │       │   ├── SIMPLE 02072026.xlsx
│   │   │       │   ├── SKOPOS 02062026.xlsx
│   │   │       │   ├── SOLAR ENERGIA RATING COM 13012026.xlsx
│   │   │       │   ├── SUZANO 13122023.xlsx
│   │   │       │   ├── TRIEX 26032026.xlsx
│   │   │       │   ├── TRUE 14042026.xlsx
│   │   │       │   ├── URUCUIA 23062026.xlsx
│   │   │       │   ├── VITOL POWER 20072026.xlsx
│   │   │       │   └── WD AGROINDUSTRIAL 13072026.xlsx
│   │   │       ├── processados/
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
│   │   │       └── rejeitados/
│   │   │           ├── GERDAU SA RATING 12122025.xlsx
│   │   │           └── QAIR BRASIL RATING 09012026.xlsx
│   │   ├── consumidores/
│   │   │   ├── pendentes/
│   │   │   ├── processadas/
│   │   │   │   ├── 3R PETROLEUM  22042024.xlsx
│   │   │   │   ├── 3R PETROLEUM 13082025.xlsx
│   │   │   │   ├── A 100 ROW Serviços de Dados 10082023.xlsx
│   │   │   │   ├── ACO CEARENSE RATING 07012026.xlsx
│   │   │   │   ├── ACUCAREIRA ZILOR 27032026.xlsx
│   │   │   │   ├── ADECOAGRO 10042026.xlsx
│   │   │   │   ├── AEBES HEJSN 01122023.xlsx
│   │   │   │   ├── AEGEA 17072025.xlsx
│   │   │   │   ├── AEGEA 20-07-2022.xlsx
│   │   │   │   ├── AEGEA SANEAMENTO 23072026.xlsx
│   │   │   │   ├── AEGEA_RIO4_16122024.xlsx
│   │   │   │   ├── Aeroporto Confins 25032025.xlsx
│   │   │   │   ├── AEROPORTO DE GUARULHOS 28082025.xlsx
│   │   │   │   ├── AEROPORTOS DO NORDESTE_16032023.xlsx
│   │   │   │   ├── AGRONORTE RATING 02032026.xlsx
│   │   │   │   ├── AGROPÉU 18062025.xlsx
│   │   │   │   ├── AGUAS DO RIO 4.xlsx
│   │   │   │   ├── AHLSTROM-MUNKSJO 27052026.xlsx
│   │   │   │   ├── ALBRAS 21072026.xlsx
│   │   │   │   ├── ALBRAS 27052025.xlsx
│   │   │   │   ├── ALCOA 08042026.xlsx
│   │   │   │   ├── ALCOA ALUMINIO 30052025.xlsx
│   │   │   │   ├── ALCOESTE BIOENERTIA 04-05-2026.xlsx
│   │   │   │   ├── ALCOESTE FERNANDÓPOLIS 22052026.xlsx
│   │   │   │   ├── ALIANSCE SONAE_29062023.xlsx
│   │   │   │   ├── ALIANÇA GERAÇÃO 17072025.xlsx
│   │   │   │   ├── ALLIANCE RATING 04022025.xlsx
│   │   │   │   ├── ALUNORTE 17062026.xlsx
│   │   │   │   ├── ALUNORTE RATING 18122025.xlsx
│   │   │   │   ├── AMBIENTAL - NESTOR DE BARROS 31072026.xlsx
│   │   │   │   ├── AMELPLAST RATING 29012026.xlsx
│   │   │   │   ├── Anglo Amercia 27022024 v2.xlsx
│   │   │   │   ├── Anglo Amercia 27022024.xlsx
│   │   │   │   ├── ANGLO AMERICAN 03072026.xlsx
│   │   │   │   ├── ANGLO AMERICAN 31.12.2023.xlsx
│   │   │   │   ├── ANGLO AMERICAN RATING 14102025.xlsx
│   │   │   │   ├── APERAM RATING 18032026.xlsx
│   │   │   │   ├── ARAMART 28072026.xlsx
│   │   │   │   ├── ARAUCO - 27032025.xlsx
│   │   │   │   ├── ARCELORMITTAL - 00350481.xlsx
│   │   │   │   ├── ARCELORMITTAL 13052026.xlsx
│   │   │   │   ├── ARCELORMITTAL RATING 05112025.xlsx
│   │   │   │   ├── Ardagh Metal 26_09_2022.xlsx
│   │   │   │   ├── ARLANXEO_21032023.xlsx
│   │   │   │   ├── ASCENTY 09072025.xlsx
│   │   │   │   ├── ASCENTY 21052026.xlsx
│   │   │   │   ├── ASCENTY RATING 13102023.xlsx
│   │   │   │   ├── ASSAI ATACADISTA 25.07.2024.xlsx
│   │   │   │   ├── ASSAI RATING 09032026.xlsx
│   │   │   │   ├── Assaí atacadista 25032025.xlsx
│   │   │   │   ├── Assaí Atacadista_24072023.xlsx
│   │   │   │   ├── Associação do Hospital de Jaragiuá - Avaliação Middle.xlsx
│   │   │   │   ├── Associação Hospitalar Santana - Avaliação Middle.xlsx
│   │   │   │   ├── ASUN RATING 24102025.xlsx
│   │   │   │   ├── ATVOS BIOENERGIA BRENCO RATING 22122025.xlsx
│   │   │   │   ├── ATVOS BIOENERGIA CONQUISTA DO PONTAL RATING 23122025.xlsx
│   │   │   │   ├── ATVOS BIOENERGIA ELDORADO RATING 22122025.xlsx
│   │   │   │   ├── ATVOS BIOENERGIA RIO CLARO RATING 23122025.xlsx
│   │   │   │   ├── ATVOS BIOENERGIA SANTA LUZIA.xlsx
│   │   │   │   ├── AURORA 10082023.xlsx
│   │   │   │   ├── AURORA ALIMENTOS 20072026.xlsx
│   │   │   │   ├── AUTODROMO ENERGÉTICA 13062025.xlsx
│   │   │   │   ├── AVENORTE_20092023.xlsx
│   │   │   │   ├── AVENORTE_30062023.xlsx
│   │   │   │   ├── BALL_02032023.xlsx
│   │   │   │   ├── BASF 14072026.xlsx
│   │   │   │   ├── BASF 25082025.xlsx
│   │   │   │   ├── BASF RATING 14102025.xlsx
│   │   │   │   ├── BE8 RATING 11122025.xlsx
│   │   │   │   ├── BE8_26_08_2024.xlsx
│   │   │   │   ├── BELLO_01062023.xlsx
│   │   │   │   ├── BERNECK 03072025.xlsx
│   │   │   │   ├── BERNECK 08102025.xlsx
│   │   │   │   ├── Bimbo_02_09_2024.xlsx
│   │   │   │   ├── Bioagri Laboratórios_03-10-2022.xlsx
│   │   │   │   ├── BIOENERGIA BARRA_30062023.xlsx
│   │   │   │   ├── BIOHOSP 15072026.xlsx
│   │   │   │   ├── BIORIGIN 15072026.xlsx
│   │   │   │   ├── BO PAPER 02062026.xlsx
│   │   │   │   ├── BO Paper 04_05_2022.xlsx
│   │   │   │   ├── BO PAPER RATING 13102025.xlsx
│   │   │   │   ├── BOA FÉ ENERGÉTICA 12062025.xlsx
│   │   │   │   ├── BOPAPER_2023_05_11.xlsx
│   │   │   │   ├── BOZEL 24062026.xlsx
│   │   │   │   ├── BOZEL BRASIL 21082025.xlsx
│   │   │   │   ├── BRACELL CELULOSE 04082025.xlsx
│   │   │   │   ├── BRADESCO_21_02_2022.xlsx
│   │   │   │   ├── BRANCO PERES 04052026.xlsx
│   │   │   │   ├── BRASFRIGO 15062026.xlsx
│   │   │   │   ├── Brasil Tropical 13072023.xlsx
│   │   │   │   ├── BRASKEM - 05 04 2024.xlsx
│   │   │   │   ├── BRASKEM 21052026.xlsx
│   │   │   │   ├── BRASKEM 22072025.xlsx
│   │   │   │   ├── Brasken 01022024 sem eprotocolo.xlsx
│   │   │   │   ├── Brastex - Avaliação Middle.xlsx
│   │   │   │   ├── Brastex 10062024.xlsx
│   │   │   │   ├── BRASTEX RATING 08012026.xlsx
│   │   │   │   ├── Braswell.xlsx
│   │   │   │   ├── BRAVA 15052026.xlsx
│   │   │   │   ├── BRAVOX_31072023.xlsx
│   │   │   │   ├── BRF 12082024.xlsx
│   │   │   │   ├── BRF FOODS 22072025.xlsx
│   │   │   │   ├── BRF RATING 01122025.xlsx
│   │   │   │   ├── Bridgestone do Brasil.xlsx
│   │   │   │   ├── Bridgestone_24_08_2022 - 2.xlsx
│   │   │   │   ├── Bridgestone_24_08_2022 - 3.xlsx
│   │   │   │   ├── Bridgestone_24_08_2022 - 4.xlsx
│   │   │   │   ├── BRK Ambiental - Avaliação Middle.xlsx
│   │   │   │   ├── BUNGE 09102025.xlsx
│   │   │   │   ├── BUNGE 18062026.xlsx
│   │   │   │   ├── C. VALE 25052026.xlsx
│   │   │   │   ├── C. VALE RATING 07112025.xlsx
│   │   │   │   ├── CAERN_23042025.xlsx
│   │   │   │   ├── CAESB RATING 20012026.xlsx
│   │   │   │   ├── CAMPO BELO G1 CARLOS CALDEIRA 30072026.xlsx
│   │   │   │   ├── CANDEIAS 15102025.xlsx
│   │   │   │   ├── CANOINHAS 17072025.xlsx
│   │   │   │   ├── Caramuru 2022-07-18.xlsx
│   │   │   │   ├── Cargil 05.08.2024.xlsx
│   │   │   │   ├── Cargil 28022024.xlsx
│   │   │   │   ├── CARGILL 11062026 - REVISÃO.xlsx
│   │   │   │   ├── CARGILL 15072025.xlsx
│   │   │   │   ├── CARGILL RATING 13102025.xlsx
│   │   │   │   ├── CBA - Cia Brasileira de Alumínio 2022-07-12.xlsx
│   │   │   │   ├── CBA 08102025 RATING RETIFICADO.xlsx
│   │   │   │   ├── CBA 08102025.xlsx
│   │   │   │   ├── CBA 24062026.xlsx
│   │   │   │   ├── CEDAE_23082023.xlsx
│   │   │   │   ├── CEEE RATING 02122025.xlsx
│   │   │   │   ├── CEEE-G_02_06_2025.xlsx
│   │   │   │   ├── CEESAM 11-12-2025.xlsx
│   │   │   │   ├── CELETRO 08072026.xlsx
│   │   │   │   ├── Centrais Eólicas de Caetité Participações S.A. 21012026.xlsx
│   │   │   │   ├── CENTRAL PACK 24082023.xlsx
│   │   │   │   ├── CEPASA 08072025.xlsx
│   │   │   │   ├── Ceramica_Formigres_18_01_2022.xlsx
│   │   │   │   ├── CERMISSOES 17082026.xlsx
│   │   │   │   ├── CERTAJA 12082026.xlsx
│   │   │   │   ├── CERTHIL 17082026.xlsx
│   │   │   │   ├── CERÂMICA ELISABETH.xlsx
│   │   │   │   ├── Cessão Flexoprint para All4Labels.xlsx
│   │   │   │   ├── CIA Sulamericana de Distribuição sem eprotocolo.xlsx
│   │   │   │   ├── Cimento Campeão Alvorada_14_01_2022.xlsx
│   │   │   │   ├── CIMENTO ITAMBE 27_07_2022.xlsx
│   │   │   │   ├── CISER 11092025.xlsx
│   │   │   │   ├── CITROSUCO_10042025.xlsx
│   │   │   │   ├── CJ DO BRASIL 01072026.xlsx
│   │   │   │   ├── CJ do Brasil_13042023.xlsx
│   │   │   │   ├── CLUBE CURITIBANO 06052026.xlsx
│   │   │   │   ├── COAMO 02062025.xlsx
│   │   │   │   ├── COAMO 11012024.xlsx
│   │   │   │   ├── COASUL RATING 31102025.xlsx
│   │   │   │   ├── Coca-cola FEMSA 05032024.xlsx
│   │   │   │   ├── COCA-COLA FEMSA RATING 25032026.xlsx
│   │   │   │   ├── Cocamar 01022024 sem eprotocolo.xlsx
│   │   │   │   ├── COCAMAR 11012024.xlsx
│   │   │   │   ├── COCAMAR 27-04-2026.xlsx
│   │   │   │   ├── Cocamar 28022024.xlsx
│   │   │   │   ├── COFCO 16042026.xlsx
│   │   │   │   ├── COFCO 21072026.xlsx
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
│   │   │   │   ├── COOPERALFA 27052026.xlsx
│   │   │   │   ├── COOPERALIANCA 11012024.xlsx
│   │   │   │   ├── COOPERALIANÇA 01102024.xlsx
│   │   │   │   ├── Cooperativa AGRARIA 28032024.xlsx
│   │   │   │   ├── COOPERATIVA REGIONAL AURIVERDE RATING 12032026.xlsx
│   │   │   │   ├── COOPERLUZ 14082026.xlsx
│   │   │   │   ├── COOPERVAL 14072026.xlsx
│   │   │   │   ├── COPACOL 18082023.xlsx
│   │   │   │   ├── COPACOL 19082026.xlsx
│   │   │   │   ├── COPACOL RATING 24102025.xlsx
│   │   │   │   ├── COPACOL_25_08_2022 - 1.xlsx
│   │   │   │   ├── COPACOL_25_08_2022 - 2.xlsx
│   │   │   │   ├── COPAPA RATING 17112025.xlsx
│   │   │   │   ├── COPAVEL RATING 11112025.xlsx
│   │   │   │   ├── COPREL 18082026.xlsx
│   │   │   │   ├── Corteva 15_08_2022.xlsx
│   │   │   │   ├── Costa e Palu 16_08_2022.xlsx
│   │   │   │   ├── CP KELKO RATING 02022026.xlsx
│   │   │   │   ├── CPIC 02_02_2023.xlsx
│   │   │   │   ├── CPTM 21072025.xlsx
│   │   │   │   ├── CPTM 25062026.xlsx
│   │   │   │   ├── CRELUZ_09102024.xlsx
│   │   │   │   ├── CRIUVA ENERGETICA 12062025.xlsx
│   │   │   │   ├── CSN 04062025.xlsx
│   │   │   │   ├── CSN 19062026.xlsx
│   │   │   │   ├── CSN 31-07-224.xlsx
│   │   │   │   ├── CSN CIMENTOS 08072025.xlsx
│   │   │   │   ├── CSN MINERAÇÃO 22082025.xlsx
│   │   │   │   ├── CVALE_09032023.xlsx
│   │   │   │   ├── DAE SA AGUA E ESGOTO 18082023.xlsx
│   │   │   │   ├── DANGLASS 29062026.xlsx
│   │   │   │   ├── DAUS ALIMENTOS RATING 16032026.xlsx
│   │   │   │   ├── Delta Indústria Cerâmica 28022025.xlsx
│   │   │   │   ├── DEXCO - 15.07.2024.xlsx
│   │   │   │   ├── DEXCO 14072025.xlsx
│   │   │   │   ├── DEXCO 22062026.xlsx
│   │   │   │   ├── DEXCO S.A._30-06-2022.xlsx
│   │   │   │   ├── DEXCO_28032023.xlsx
│   │   │   │   ├── Diagnósticos da América 08042025.xlsx
│   │   │   │   ├── DIP FRANGOS - 21072025.xlsx
│   │   │   │   ├── DIP FRANGOS 28042026.xlsx
│   │   │   │   ├── Dois Marcos Sementes 03042024.xlsx
│   │   │   │   ├── Dulce Acqua_28_09_2022.xlsx
│   │   │   │   ├── DUPATRI HOSPITALAR.xlsx
│   │   │   │   ├── DUPLAS RATING 09022026.xlsx
│   │   │   │   ├── EATON_23_02_2022.xlsx
│   │   │   │   ├── ECOURBIS - 17062026.xlsx
│   │   │   │   ├── EDF 24072025 v2.xlsx
│   │   │   │   ├── EDF VERDECOM RATING 17102025.xlsx
│   │   │   │   ├── ELEKEIROZ 15052024.xlsx
│   │   │   │   ├── ELEKEIROZ 19082026.xlsx
│   │   │   │   ├── ELEKEIROZ_15_08_2024.xlsx
│   │   │   │   ├── Eletrobras_30052025.xlsx
│   │   │   │   ├── ELFA MEDICAMENTOS 22052026.xlsx
│   │   │   │   ├── Elizabeth Porcelanato.xlsx
│   │   │   │   ├── EMBASA 14042025.xlsx
│   │   │   │   ├── EMBASA 18062026.xlsx
│   │   │   │   ├── EMBRAER 05052026.xlsx
│   │   │   │   ├── EMBRAER_10042023.xlsx
│   │   │   │   ├── ENERPEIXE 15092025.xlsx
│   │   │   │   ├── Engetech 10032025.xlsx
│   │   │   │   ├── EPASA 21122023.xlsx
│   │   │   │   ├── ESTADO DE SP 15_08_2022.xlsx
│   │   │   │   ├── ETERNIT RATING 18122025.xlsx
│   │   │   │   ├── EUCATEX RATING 28102025.xlsx
│   │   │   │   ├── EUROFARMA_03102023.xlsx
│   │   │   │   ├── EVONIK 04112024.xlsx
│   │   │   │   ├── EVONIK 13082025.xlsx
│   │   │   │   ├── EVONIK 29052026.xlsx
│   │   │   │   ├── EVONIK_16062023.xlsx
│   │   │   │   ├── EVONIK_FILIAL 04112024.xlsx
│   │   │   │   ├── EXTRAMIX - Avaliação Middle.xlsx
│   │   │   │   ├── EXTRUSAICK 17062026.xlsx
│   │   │   │   ├── FACCHINI SA 22122025.xlsx
│   │   │   │   ├── FACCHINI_20022025.xlsx
│   │   │   │   ├── FACULDADES ALFA RATING 29102025.xlsx
│   │   │   │   ├── FCA Fiat-Chrysler_22_08_2022.xlsx
│   │   │   │   ├── FERBASA 00355224.xlsx
│   │   │   │   ├── FERBASA 28052026.xlsx
│   │   │   │   ├── FERNANDEZ INDUSTRIA DE PAPEL RATING 09032026.xlsx
│   │   │   │   ├── FGV 15102025.xlsx
│   │   │   │   ├── Fiação São Bento 08_11_2022.xlsx
│   │   │   │   ├── FIBRAPLAC_12_08_2024.xlsx
│   │   │   │   ├── ficha ARAUCO 2022.xlsx
│   │   │   │   ├── ficha BASF 2022.xlsx
│   │   │   │   ├── FICHA CONSUMIDORES V1 (2)_VALE_PREENCHIDA 3.xlsx
│   │   │   │   ├── ficha FERBASA 2022.xlsx
│   │   │   │   ├── FICHA MODELO ddmmaaaa.xlsx
│   │   │   │   ├── ficha modelo livres acima de 2MWm.xlsx
│   │   │   │   ├── ficha SANTHER 2022-10.xlsx
│   │   │   │   ├── ficha São Eutiquiano Participações (Grupo Maringá) 2022.xlsx
│   │   │   │   ├── ficha Yara Brasil Fertilizantes SA 2022.xlsx
│   │   │   │   ├── FICHA_CONSUMIDORES_AMSTED_MAXXION_PREENCHIDA.xlsx
│   │   │   │   ├── FICHA_CONSUMIDORES_CORSAN_PREENCHIDA.xlsx
│   │   │   │   ├── FICHA_CONSUMIDORES_FS_BIOENERGIA_CORRIGIDA_PCF.xlsx
│   │   │   │   ├── FICHA_CONSUMIDORES_GV_DO_BRASIL_FINAL.xlsx
│   │   │   │   ├── FICHA_CONSUMIDORES_MILI_SA_PREENCHIDA.xlsx
│   │   │   │   ├── FICHA_CONSUMIDORES_UNIMED_SOROCABA_PREENCHIDA 2.xlsx
│   │   │   │   ├── FICHA_CONSUMIDORES_V1_CEESAM_PREENCHIDA 1.xlsx
│   │   │   │   ├── Fontain 05032024.xlsx
│   │   │   │   ├── FOSNOR 20-02-225.xlsx
│   │   │   │   ├── Frigoestrela_02052023.xlsx
│   │   │   │   ├── FRIGOESTRELA_20_08_2024.xlsx
│   │   │   │   ├── FRIMESA - 08 04 2024.xlsx
│   │   │   │   ├── FRISIA_03102023.xlsx
│   │   │   │   ├── GAB 10012024.xlsx
│   │   │   │   ├── GAZIT 05022024.xlsx
│   │   │   │   ├── GERDAU ACOMINAS RATING 11122025.xlsx
│   │   │   │   ├── GERDAU ACOS LONGOS - 00482085.xlsx
│   │   │   │   ├── GERDAU Açominas 11122024.xlsx
│   │   │   │   ├── GERDAU Aços Longos 11122024.xlsx
│   │   │   │   ├── GERDAU AÇOS LONGOS 13062025.xlsx
│   │   │   │   ├── GERDAU AÇOS LONGOS RATING 15102025.xlsx
│   │   │   │   ├── GERDAU MATRIZ 20052026.xlsx
│   │   │   │   ├── GERDAU SA - 13062025.xlsx
│   │   │   │   ├── GERDAU SA 11122024.xlsx
│   │   │   │   ├── GERDAU_23062023.xlsx
│   │   │   │   ├── Globalpack 17012024.xlsx
│   │   │   │   ├── GM do Brasil - Avaliação Middle.xlsx
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
│   │   │   │   ├── GTFOODS 15072026.xlsx
│   │   │   │   ├── GTOP RATING 12122025.xlsx
│   │   │   │   ├── GUERRO 08042024.xlsx
│   │   │   │   ├── GWEST RATING 03022026.xlsx
│   │   │   │   ├── HAVAN - 08082025.xlsx
│   │   │   │   ├── HAVAN SA 06042026.xlsx
│   │   │   │   ├── Heinz Brasil - Avaliação Middle.xlsx
│   │   │   │   ├── HEINZ_20032023.xlsx
│   │   │   │   ├── HEJSN_19_10_2022.xlsx
│   │   │   │   ├── HF SISTEMAS DE FREIOS RATING 26012026.xlsx
│   │   │   │   ├── Hospital Cruz Vermelha - Avaliação Middle.xlsx
│   │   │   │   ├── HOSPITAL EVANLEGICO DE LONDRINA 20072026.xlsx
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
│   │   │   │   ├── INDEMIL RATING 23032026 - Copia.xlsx
│   │   │   │   ├── INDUPA 19052026.xlsx
│   │   │   │   ├── INDUPA RATING 03112025.xlsx
│   │   │   │   ├── INDUSTRIA VIDREIRA DO NORDESTE RATING 04022026.xlsx
│   │   │   │   ├── INPASA RATING 10122025.xlsx
│   │   │   │   ├── Intercast - Avaliação Middle.xlsx
│   │   │   │   ├── INTERCEMENT - 08072025.xlsx
│   │   │   │   ├── INTERCEMENT RATING 13102025.xlsx
│   │   │   │   ├── INTERCEMENT RATING 19032026.xlsx
│   │   │   │   ├── InterCement_20_10_2022.xlsx
│   │   │   │   ├── IPIRANGA AGROINDUSTRIAL 0605026.xlsx
│   │   │   │   ├── IRANI_07-07-2022.xlsx
│   │   │   │   ├── Itambe 03042024.xlsx
│   │   │   │   ├── ITAMBE CIMENTOS 24072026.xlsx
│   │   │   │   ├── ITAMBE ENERGETICA SA 18082025.xlsx
│   │   │   │   ├── Jacobina Mineração_24_02_2023.xlsx
│   │   │   │   ├── JAGUAFRANGOS 08012024.xlsx
│   │   │   │   ├── Jardim Botânico Participações 28-10-2025.xlsx
│   │   │   │   ├── JBS 11012024.xlsx
│   │   │   │   ├── JBS 13052026.xlsx
│   │   │   │   ├── JBS SA - 08072025.xlsx
│   │   │   │   ├── JBSFILIAL_01102024.xlsx
│   │   │   │   ├── KARSTEN - 15.07.2024.xlsx
│   │   │   │   ├── Karsten 12_09_2022.xlsx
│   │   │   │   ├── KARSTEN SA 09102025.xlsx
│   │   │   │   ├── Kimberly-Clark análises.xlsx
│   │   │   │   ├── KINROSS 28102025.xlsx
│   │   │   │   ├── Klabin 03112023.xlsx
│   │   │   │   ├── Klabin 12062024.xlsx
│   │   │   │   ├── KLABIN 15052026.xlsx
│   │   │   │   ├── KLABIN 18_02_2022.xlsx
│   │   │   │   ├── Klabin 26032025.xlsx
│   │   │   │   ├── KORDSA_13032025.xlsx
│   │   │   │   ├── KORDSA_20_04_2022.xlsx
│   │   │   │   ├── KRONA TUBOS e CONEXOES 28042025.xlsx
│   │   │   │   ├── LAR COOPERATIVA 03072025.xlsx
│   │   │   │   ├── LAR COOPERATIVA 07012024 v2.xlsx
│   │   │   │   ├── Laticínios Ruhban 09102025.xlsx
│   │   │   │   ├── LDC 09102025 RATING.xlsx
│   │   │   │   ├── LDC BRASIL 30062025.xlsx
│   │   │   │   ├── LDC MATRIZ.xlsx
│   │   │   │   ├── LDC SUCOS 06052026.xlsx
│   │   │   │   ├── LDC SUCOS 30062025.xlsx
│   │   │   │   ├── LDC TES 10102025 RATING.xlsx
│   │   │   │   ├── LDC TES 30062025.xlsx
│   │   │   │   ├── LIASA 05012024 v2.xlsx
│   │   │   │   ├── LIASA 18062025.xlsx
│   │   │   │   ├── LIASA RATING 24102025.xlsx
│   │   │   │   ├── LIBRA LIGAS - 08 04 2024.xlsx
│   │   │   │   ├── LIBRAS RATING 09032026.xlsx
│   │   │   │   ├── LIGA ALVARO BAHIA RATING 03112025.xlsx
│   │   │   │   ├── LINHA 4 - MOTIVA 06072026.xlsx
│   │   │   │   ├── LINHAS 5 E 17 06072026.xlsx
│   │   │   │   ├── LINHAS 8 E 9 07072026.xlsx
│   │   │   │   ├── LSNC RATING 12122025.xlsx
│   │   │   │   ├── LUME CERAMICA 14042026.xlsx
│   │   │   │   ├── LYCRA_22062023.xlsx
│   │   │   │   ├── LÍDER (Atacadista) 02122024.xlsx
│   │   │   │   ├── M DIAS BRANCO 08062026.xlsx
│   │   │   │   ├── M DIAS BRANCO 15082025.xlsx
│   │   │   │   ├── MAHLE 13082026.xlsx
│   │   │   │   ├── MARFRIG RATING 05112025.xlsx
│   │   │   │   ├── MARINGA FERRO LIGA 18062026.xlsx
│   │   │   │   ├── MARINGA FERRO LIGA 26082025.xlsx
│   │   │   │   ├── MBRF_09062026.xlsx
│   │   │   │   ├── MESSER GASES 02072025.xlsx
│   │   │   │   ├── Messer Gases 16112023.xlsx
│   │   │   │   ├── MESSER GASES 22072026.xlsx
│   │   │   │   ├── MESSER GASES_05052022.xlsx
│   │   │   │   ├── MESSER_27_12_2022.xlsx
│   │   │   │   ├── METAL LEVE - 21082025.xlsx
│   │   │   │   ├── METALBRAZING 11062026.xlsx
│   │   │   │   ├── METRO 15072025.xlsx
│   │   │   │   ├── METRO BAHIA 08102025.xlsx
│   │   │   │   ├── Metro Bahia 18042024.xlsx
│   │   │   │   ├── METRO BAHIA 21082025.xlsx
│   │   │   │   ├── METRO RIO 13082025.xlsx
│   │   │   │   ├── METRO SP 23062026.xlsx
│   │   │   │   ├── METRORIO 30062026.xlsx
│   │   │   │   ├── MetroRio_06042023.xlsx
│   │   │   │   ├── Metrô São Paulo_06032023.xlsx
│   │   │   │   ├── MHC PLASTICOS 28072025.xlsx
│   │   │   │   ├── MILI RATING 19112025.xlsx
│   │   │   │   ├── MINASLIGAS 07052026.xlsx
│   │   │   │   ├── MINERACAO ONCA PUMA 17082026.xlsx
│   │   │   │   ├── MINERACAO ONCA PUMA RATING 03112025.xlsx
│   │   │   │   ├── MINERACAO RIO DO NORTE 16062026.xlsx
│   │   │   │   ├── MINERACAO RIO DO NORTE SA.xlsx
│   │   │   │   ├── MINERACAO USMINAS 13082026.xlsx
│   │   │   │   ├── Mineração Aurizona 17052024.xlsx
│   │   │   │   ├── MINERAÇÃO AURIZONA 23082023.xlsx
│   │   │   │   ├── MINERAÇÃO PARAGOMINAS - 07082025.xlsx
│   │   │   │   ├── Minerva 01112023.xlsx
│   │   │   │   ├── MINING CORUMBA RATING 28012026.xlsx
│   │   │   │   ├── Moinho Itaipu 29062025.xlsx
│   │   │   │   ├── MOTIVA RATING 25102025.xlsx
│   │   │   │   ├── MOTIVA SA 13082026.xlsx
│   │   │   │   ├── Muffato 07112023.xlsx
│   │   │   │   ├── NADIR FIGUEIREDO 02042026.xlsx
│   │   │   │   ├── NATURAFRIG RATING 20022026.xlsx
│   │   │   │   ├── NEXA 05012026.xlsx
│   │   │   │   ├── NEXA 08072025.xlsx
│   │   │   │   ├── NEXA RECURSOS MINERAIS 18062026.xlsx
│   │   │   │   ├── Nitaplast 16_08_2022.xlsx
│   │   │   │   ├── NORFIL 13062025.xlsx
│   │   │   │   ├── NORFIL 15022024.xlsx
│   │   │   │   ├── NORFIL SA 27042026.xlsx
│   │   │   │   ├── NORFIL_13_01_23.xlsx
│   │   │   │   ├── NOVA FIAÇAO 14052026.xlsx
│   │   │   │   ├── NOVELIS 05062026.xlsx
│   │   │   │   ├── NOVELIS 08052026.xlsx
│   │   │   │   ├── NOVO ATACAREJO 28102025.xlsx
│   │   │   │   ├── Oggi Alimentos_13_10_2022.xlsx
│   │   │   │   ├── ORIZON 25092025.xlsx
│   │   │   │   ├── OXITENO 24062026.xlsx
│   │   │   │   ├── PADO_28062023.xlsx
│   │   │   │   ├── PAPIRUS RATING 25022026.xlsx
│   │   │   │   ├── PARAGOMINAS 03082026.xlsx
│   │   │   │   ├── PARANA BOI 24042026.xlsx
│   │   │   │   ├── Paraná Xisto 13012025.xlsx
│   │   │   │   ├── Paraná Xisto 22082023.xlsx
│   │   │   │   ├── PB Gelatinas_03_10_2022.xlsx
│   │   │   │   ├── PEROXIDOS 28-04-2026.xlsx
│   │   │   │   ├── Peróxidos_24_02_2023.xlsx
│   │   │   │   ├── PETROBRAS 10062026.xlsx
│   │   │   │   ├── PETROBRAS RATING 10112025.xlsx
│   │   │   │   ├── PETRORECONCAVO 08052026.xlsx
│   │   │   │   ├── PETRORECONCAVO RATING 11112025.xlsx
│   │   │   │   ├── PLASTICOS AMSTERDAN 13072026.xlsx
│   │   │   │   ├── PM Cascavel.xlsx
│   │   │   │   ├── POLIMIX_06062023.xlsx
│   │   │   │   ├── POLO FILMS 20-07-2022.xlsx
│   │   │   │   ├── PORTO ITAPOA RATING 10122025.xlsx
│   │   │   │   ├── PRATI DONADUZI 14072026.xlsx
│   │   │   │   ├── PRATI DONADUZZI 24082023.xlsx
│   │   │   │   ├── Prati Donaduzzi_24_06_2022.xlsx
│   │   │   │   ├── PRIMA FOODS RATING 27012026.xlsx
│   │   │   │   ├── PURO PELLET - Avaliação Middle.xlsx
│   │   │   │   ├── QAIR 02072025.xlsx
│   │   │   │   ├── Quimica Amparo YPE - Avaliação Middle.xlsx
│   │   │   │   ├── RAIZEN_20092023.xlsx
│   │   │   │   ├── RANDON 03082026.xlsx
│   │   │   │   ├── RANDON 04032024.xlsx
│   │   │   │   ├── Raízen Geo Biogás 13022025.xlsx
│   │   │   │   ├── REDE DOR SÃO LUIZ.xlsx
│   │   │   │   ├── REFINARIA MATARIPE 17082026.xlsx
│   │   │   │   ├── REPINHO 01072025.xlsx
│   │   │   │   ├── REPINHO 29042025.xlsx
│   │   │   │   ├── RHODIA BRASIL 20072026.xlsx
│   │   │   │   ├── RIACHUELO_05072023.xlsx
│   │   │   │   ├── RIMA INDSUTRIAL 07072025.xlsx
│   │   │   │   ├── RIMA INDUSTRIAL RATING 04112025.xlsx
│   │   │   │   ├── Rio de Janeiro Refrescos - Avaliação Middle.xlsx
│   │   │   │   ├── Rio de Janeiro Refrescos 16102023.xlsx
│   │   │   │   ├── RIO GALEAO RATING 04112025.xlsx
│   │   │   │   ├── RIO PARANÁ ENERGIA 26112024.xlsx
│   │   │   │   ├── ROMI 16052025.xlsx
│   │   │   │   ├── RUY ROCHA 30042026.xlsx
│   │   │   │   ├── RVTRANS 31072026.xlsx
│   │   │   │   ├── SABESP 23062026.xlsx
│   │   │   │   ├── SABESP RATING 10112025.xlsx
│   │   │   │   ├── SALOBO METAIS 20082026.xlsx
│   │   │   │   ├── SALOBO METAIS 28072025.xlsx
│   │   │   │   ├── SAMARCO 13102025.xlsx
│   │   │   │   ├── SAMARCO 16102023.xlsx
│   │   │   │   ├── SAMARCO 21082026.xlsx
│   │   │   │   ├── SAMARCO RATING 23122025.xlsx
│   │   │   │   ├── SANEAGO_20250106.xlsx
│   │   │   │   ├── SANEPAR 02072025.xlsx
│   │   │   │   ├── SANEPAR 12012024.xlsx
│   │   │   │   ├── SANEPAR 21052026.xlsx
│   │   │   │   ├── SANEPAR RATING 17102025.xlsx
│   │   │   │   ├── SANSUY 10062025 v2.xlsx
│   │   │   │   ├── Santa Maria_11_03_2022.xlsx
│   │   │   │   ├── Santa Terezinha 24032025.xlsx
│   │   │   │   ├── SANTAHELENA_2023_03_15.xlsx
│   │   │   │   ├── Santher 01022024 sem eprotocolo.xlsx
│   │   │   │   ├── Santo Antonio Energia 01102024.xlsx
│   │   │   │   ├── SAO MARTINHO 01062026.xlsx
│   │   │   │   ├── SAO MARTINHO RATING 02022026.xlsx
│   │   │   │   ├── SCALA DATA CENTERS 0508226.xlsx
│   │   │   │   ├── SCALA DATA CENTERS 2025.xlsx
│   │   │   │   ├── SCHULZ 18082026.xlsx
│   │   │   │   ├── Segalas Alimentos - Avaliação Middle.xlsx
│   │   │   │   ├── SENDAS DISTRIBUIDORA 22_08_2022.xlsx
│   │   │   │   ├── SERLONAS RATING 10032026.xlsx
│   │   │   │   ├── SERRANA 11062025.xlsx
│   │   │   │   ├── SERVENG CIVILSAN 18082026.xlsx
│   │   │   │   ├── SERVENG CIVILSAN RATING 12112025.xlsx
│   │   │   │   ├── SHOPPING BOULEVARD RATING 16032026.xlsx
│   │   │   │   ├── SHOPPING VILHA  VELHA RATING 19032026.xlsx
│   │   │   │   ├── SINOBRAS 09072026.xlsx
│   │   │   │   ├── SLC_AGRICOLA_23_11_2022.xlsx
│   │   │   │   ├── SOFTYS BRASIL 25062025.xlsx
│   │   │   │   ├── SOFTYS_09_03_2022.xlsx
│   │   │   │   ├── SOLAR BEBIDAS SA RATING 09012026.xlsx
│   │   │   │   ├── SOLAR BR 25052026.xlsx
│   │   │   │   ├── SOLAR BR ENERGIA RATING 09012026.xlsx
│   │   │   │   ├── SOLAR ENERGIAS RATING 12122025.xlsx
│   │   │   │   ├── SOLVI ESSENCIS RATING 23032026.xlsx
│   │   │   │   ├── SONORA ESTANCIA 25052026.xlsx
│   │   │   │   ├── SOUTH32 18082026.xlsx
│   │   │   │   ├── SOUZA CRUZ RATING 04032026.xlsx
│   │   │   │   ├── spal 05032024.xlsx
│   │   │   │   ├── Sta Casa Rio Claro 17102023.xlsx
│   │   │   │   ├── Stara - Avaliação Middle.xlsx
│   │   │   │   ├── SUDATI 08042024.xlsx
│   │   │   │   ├── Sumitomo_10082023.xlsx
│   │   │   │   ├── SUPERMERCADO LIS RATING 29012026.xlsx
│   │   │   │   ├── Supremo Cimentos_02032023.xlsx
│   │   │   │   ├── Suzano 01022024 sem eprotocolo.xlsx
│   │   │   │   ├── SUZANO 29052026.xlsx
│   │   │   │   ├── SUZANO RATING 03122025.xlsx
│   │   │   │   ├── SUZANO_2023_07_03.xlsx
│   │   │   │   ├── SYLVAMO_20_07_2022.xlsx
│   │   │   │   ├── SÃO PAULO ENERGÉTICA 11062025.xlsx
│   │   │   │   ├── TCP 04082025.xlsx
│   │   │   │   ├── TCP RATING 04112025.xlsx
│   │   │   │   ├── TCP_Paranaguá_16_01_2023.xlsx
│   │   │   │   ├── TECPAR 03072024.xlsx
│   │   │   │   ├── TEREOS ACUCAR 14072026.xlsx
│   │   │   │   ├── TEREOS AMIDOS E ADOCANTES RATING 27112025.xlsx
│   │   │   │   ├── TEREOS AÇÚCAR RATING 25032026.xlsx
│   │   │   │   ├── Termomecânica São Paulo_05102023.xlsx
│   │   │   │   ├── TERNIUM 26052026.xlsx
│   │   │   │   ├── TERNIUM BRASIL 02072025.xlsx
│   │   │   │   ├── Terphane - Avaliação Middle.xlsx
│   │   │   │   ├── TERPHANE RATING 30012026.xlsx
│   │   │   │   ├── TES Terminal Exp Santos 05052026.xlsx
│   │   │   │   ├── TIGRE_27032023.xlsx
│   │   │   │   ├── TIM - Avaliação Middle.xlsx
│   │   │   │   ├── TODIMO_06122024.xlsx
│   │   │   │   ├── TRANSPETRO 08062026.xlsx
│   │   │   │   ├── TRANSPETRO 09072025.xlsx
│   │   │   │   ├── TRANSPPASS 03082026.xlsx
│   │   │   │   ├── TRANSVIDA RATING 20022026.xlsx
│   │   │   │   ├── TRENS DE SP 21082025.xlsx
│   │   │   │   ├── TROMBINI - 15.07.2024.xlsx
│   │   │   │   ├── TROMBINI 28082023.xlsx
│   │   │   │   ├── Trombini_10_11_2022.xlsx
│   │   │   │   ├── TUPY 14072025.xlsx
│   │   │   │   ├── TUPY_15052023.xlsx
│   │   │   │   ├── UHE SAO SIMAO 28082025.xlsx
│   │   │   │   ├── UNIAO OESTE 20052026.xlsx
│   │   │   │   ├── UNIDAS SUL 180052026.xlsx
│   │   │   │   ├── UNIGEL - Proquigel 30-01-2023.xlsx
│   │   │   │   ├── UNIGEL 24072025.xlsx
│   │   │   │   ├── Unilever_17112023.xlsx
│   │   │   │   ├── UNIMED 15072026.xlsx
│   │   │   │   ├── UNIMED LONDRINA.xlsx
│   │   │   │   ├── UNIPAR 19052026.xlsx
│   │   │   │   ├── UNIPAR RATING 04112025.xlsx
│   │   │   │   ├── UNIRON_10_10_2022.xlsx
│   │   │   │   ├── União Química 14112023.xlsx
│   │   │   │   ├── USIMINAS 07072025.xlsx
│   │   │   │   ├── USIMINAS 15042026.xlsx
│   │   │   │   ├── USIMINAS 25062026.xlsx
│   │   │   │   ├── USINA LATICIÍNIOS JUSSARA 08052026.xlsx
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
│   │   │   │   ├── VILLARES METALS 02072026.xlsx
│   │   │   │   ├── VILLARES METALS RATING 12112025.xlsx
│   │   │   │   ├── VILLARES_14032023.xlsx
│   │   │   │   ├── VIPAL_05042023.xlsx
│   │   │   │   ├── VIRACOPOS - 04042024.xlsx
│   │   │   │   ├── Vista Foods 15122023.xlsx
│   │   │   │   ├── Vitopel_2023_07_27.xlsx
│   │   │   │   ├── VIVIX 28_07_2022.xlsx
│   │   │   │   ├── Volks 21-07-2022.xlsx
│   │   │   │   ├── VOTORANTIM 07072025.xlsx
│   │   │   │   ├── VOTORANTIM 07072026.xlsx
│   │   │   │   ├── VOTORANTIM NNE 20082025.xlsx
│   │   │   │   ├── VOTORANTIM SA 11052026.xlsx
│   │   │   │   ├── Votorantim.xlsx
│   │   │   │   ├── VW do Brasil_18072023.xlsx
│   │   │   │   ├── WD AGROINDUSTRIAL 20052026.xlsx
│   │   │   │   ├── WEG - MATRIZ 15052026.xlsx
│   │   │   │   ├── WEG 03072025.xlsx
│   │   │   │   ├── WEG 11012024.xlsx
│   │   │   │   ├── WEG 25112024.xlsx
│   │   │   │   ├── WHB_08042024.xlsx
│   │   │   │   ├── WHB_11042024.xlsx
│   │   │   │   ├── WHIRLPOOL_24_04_2023.xlsx
│   │   │   │   ├── WHITE MARTINS 20082025.xlsx
│   │   │   │   ├── WHITE MARTINS 30072026.xlsx
│   │   │   │   └── YARA NITROGENADOS RATING 11112025.xlsx
│   │   │   ├── rejeitadas/
│   │   │   │   ├── 3R PETROLEUM RATING 19112025.xlsx
│   │   │   │   ├── AEGEA RATING 09122025.xlsx
│   │   │   │   ├── AEROPORTO DE GUARULHOS 28082025_consiste.xlsx
│   │   │   │   ├── AEROPORTO DE GUARULHOS RATING 04112025.xlsx
│   │   │   │   ├── AIR LIQUIDE 06072026.xlsx
│   │   │   │   ├── ALBRAS RATING 05012026.xlsx
│   │   │   │   ├── ALCOA ALUMINIO RATING 01122025.xlsx
│   │   │   │   ├── ALCOA WORLD 13052026.xlsx
│   │   │   │   ├── ALIANÇA GERAÇÃO RATING 28012026.xlsx
│   │   │   │   ├── ARCELORMITTAL PECEM 17072026.xlsx
│   │   │   │   ├── BASF 23062026.xlsx
│   │   │   │   ├── BOZEL RATING 31102025.xlsx
│   │   │   │   ├── BRACELL RATING 02122025.xlsx
│   │   │   │   ├── BRACELL RATING 10032025.xlsx
│   │   │   │   ├── BRASKEM RATING 24102025.xlsx
│   │   │   │   ├── CBA CIA BRASILEIRA DE ALUMINIO 30052025.xlsx
│   │   │   │   ├── CEPASA RATING 19112025.xlsx
│   │   │   │   ├── CMPC 14072026.xlsx
│   │   │   │   ├── COMPANHIA RIOGRANDENSE DE SANEAMENTO 18082025_consiste.xlsx
│   │   │   │   ├── COMPANHIA RIOGRANDENSE DE SANEAMENTO 19112025.xlsx
│   │   │   │   ├── CONSORCIO TRANSVIDA RATING 18022026.xlsx
│   │   │   │   ├── CPTM RATING 19112025.xlsx
│   │   │   │   ├── CSN CIMENTOS RATING 31102025.xlsx
│   │   │   │   ├── CSN MATRIZ RATING 06012026.xlsx
│   │   │   │   ├── CSN MINERACAO 20072026.xlsx
│   │   │   │   ├── CSN MINERAÇÃO 22082025_consiste.xlsx
│   │   │   │   ├── CSN MINERAÇÃO RATING 03112025.xlsx
│   │   │   │   ├── DEXCO RATING 19112025.xlsx
│   │   │   │   ├── DITIN 14072026.xlsx
│   │   │   │   ├── DOW BRASIL RATING 21012026.xlsx
│   │   │   │   ├── EATON LTDA RATING 12032026.xlsx
│   │   │   │   ├── EBAZAR 18062026.xlsx
│   │   │   │   ├── EDF 24072025.xlsx
│   │   │   │   ├── EDF RATING 24122025.xlsx
│   │   │   │   ├── EMBASA RATING 01122025.xlsx
│   │   │   │   ├── EVONIK RATING 19112025.xlsx
│   │   │   │   ├── FERBASA RATING 03122025.xlsx
│   │   │   │   ├── FIBRAPLAC 22102025.xlsx
│   │   │   │   ├── FICHA MODELO NOVA DDMMAA.xlsx
│   │   │   │   ├── GERDAU AÇOMINAS 13062025.xlsx
│   │   │   │   ├── GERDAU AÇOS LONGOS RATING 27032026.xlsx
│   │   │   │   ├── GERDAU SA RATING 12122025.xlsx
│   │   │   │   ├── GM RATING 16012026.xlsx
│   │   │   │   ├── GPA RATING 10032026.xlsx
│   │   │   │   ├── GTFOODS RATING 26052026.xlsx
│   │   │   │   ├── HAVAN RATING 03112025.xlsx
│   │   │   │   ├── INDEMIL RATING 23032026.xlsx
│   │   │   │   ├── INDUPA 14072025.xlsx
│   │   │   │   ├── IRGOVEL 28072026.xlsx
│   │   │   │   ├── ITAMBE MATRIZ - 17092025.xlsx
│   │   │   │   ├── ITAMBE MATRIZ RATING 16102025.xlsx
│   │   │   │   ├── JBS SA RATING 06112025.xlsx
│   │   │   │   ├── Klabin Rating 17102025.xlsx
│   │   │   │   ├── LAR COOPERATIVA RATING 18112025.xlsx
│   │   │   │   ├── LAVANDERIA JUSSARA 05052026.xlsx
│   │   │   │   ├── LDC SUCOS RATING 13112025.xlsx
│   │   │   │   ├── LIASA RATING 29102025.xlsx
│   │   │   │   ├── M DIAS BRANCO 15082025_consiste.xlsx
│   │   │   │   ├── M DIAS BRANCO RATING 03112025.xlsx
│   │   │   │   ├── MARINGA FERRO LIGA RATING 31102025.xlsx
│   │   │   │   ├── MESSES GASES RATING 12112025.xlsx
│   │   │   │   ├── METAL LEVE RATING 18022026.xlsx
│   │   │   │   ├── METAL LEVE RATING 31102025.xlsx
│   │   │   │   ├── METRO BAHIA RATING 19112025.xlsx
│   │   │   │   ├── METRO RATING 26112025.xlsx
│   │   │   │   ├── METRO RIO RATING 03112025.xlsx
│   │   │   │   ├── MICHELIN RATING 15012026.xlsx
│   │   │   │   ├── MILI SA 05082025.xlsx
│   │   │   │   ├── MOSAIC FERTILIZANTES RATING 21012026.xlsx
│   │   │   │   ├── MOTIVA 19062026.xlsx
│   │   │   │   ├── MOTIVA SA 23062026.xlsx
│   │   │   │   ├── NADIR FIGUEIREDO 21072026.xlsx
│   │   │   │   ├── NC COMUNICACOES RATING 27022026.xlsx
│   │   │   │   ├── NEXA RATING 05012026.xlsx
│   │   │   │   ├── ORIZON RATING 25112025.xlsx
│   │   │   │   ├── PARACATU RATING 04032026.xlsx
│   │   │   │   ├── PARAGOMINAS RATING 18112025.xlsx
│   │   │   │   ├── QAIR BRASIL RATING 09012026.xlsx
│   │   │   │   ├── RAIZEN 16042026.xlsx
│   │   │   │   ├── ROMI RATING 31102025.xlsx
│   │   │   │   ├── ROMI_24062025.xlsx
│   │   │   │   ├── SABESP_27052025.xlsx
│   │   │   │   ├── SALOBO METAIS RATING 12112025.xlsx
│   │   │   │   ├── SAMARCO 25082025.xlsx
│   │   │   │   ├── SANSUY 10062025.xlsx
│   │   │   │   ├── Santander 02012024.xlsx
│   │   │   │   ├── SAVOY MATRIZ 27042026.xlsx
│   │   │   │   ├── SCALA DATA CENTERS RATING 18112025.xlsx
│   │   │   │   ├── SOFTYS BRASIL RATING 03122025.xlsx
│   │   │   │   ├── SOUTH32 RATING 09122025.xlsx
│   │   │   │   ├── SUZANO_26062025.xlsx
│   │   │   │   ├── TERNIUM RATING 27102025.xlsx
│   │   │   │   ├── TRANSPETRO 25082025.xlsx
│   │   │   │   ├── TRANSPETRO 25082025_consiste.xlsx
│   │   │   │   ├── TRANSPETRO RATING 19112025.xlsx
│   │   │   │   ├── TUPY RATING 19112025.xlsx
│   │   │   │   ├── URUCUIA GERAÇÃO 20082025.xlsx
│   │   │   │   ├── USIMINAS RATING 05112025.xlsx
│   │   │   │   ├── USINAGEM TIMBO RATING 05022026.xlsx
│   │   │   │   ├── VALE 20072026.xlsx
│   │   │   │   ├── VALE RATING 04112025.xlsx
│   │   │   │   ├── VOLKSWAGEN RATING 08012026.xlsx
│   │   │   │   ├── VOTORANTIM CIMENTOS RATING.xlsx
│   │   │   │   ├── VOTORANTIM NNE 20082025_consiste.xlsx
│   │   │   │   ├── VOTORANTIM NNE RATING 22122025.xlsx
│   │   │   │   ├── VOTORANTIM RATING 05112025.xlsx
│   │   │   │   ├── VTAL Rede Neutra 23072025.xlsx
│   │   │   │   ├── WEG RATING 04112025.xlsx
│   │   │   │   ├── WHITE MARTINS RATING 30102025.xlsx
│   │   │   │   ├── YARA 13072026.xlsx
│   │   │   │   └── ZILOR 27052026.xlsx
│   │   │   └── reprocessamento/
│   │   │       ├── pendentes/
│   │   │       ├── processadas/
│   │   │       │   ├── ADECOAGRO 10042026.xlsx
│   │   │       │   ├── AEGEA SANEAMENTO 23072026.xlsx
│   │   │       │   ├── AHLSTROM-MUNKSJO 27052026.xlsx
│   │   │       │   ├── ALBRAS 21072026.xlsx
│   │   │       │   ├── ALCOA 08042026.xlsx
│   │   │       │   ├── ALCOESTE FERNANDÓPOLIS 22052026.xlsx
│   │   │       │   ├── ALLIANCE RATING 04022025.xlsx
│   │   │       │   ├── ALUNORTE 17062026.xlsx
│   │   │       │   ├── AMBIENTAL - NESTOR DE BARROS 31072026.xlsx
│   │   │       │   ├── ANGLO AMERICAN 03072026.xlsx
│   │   │       │   ├── ARAMART 28072026.xlsx
│   │   │       │   ├── ASCENTY 21052026.xlsx
│   │   │       │   ├── ASSAI RATING 09032026.xlsx
│   │   │       │   ├── AURORA ALIMENTOS 20072026.xlsx
│   │   │       │   ├── BASF 14072026.xlsx
│   │   │       │   ├── BIOHOSP 15072026.xlsx
│   │   │       │   ├── BIORIGIN 15072026.xlsx
│   │   │       │   ├── BO PAPER 02062026.xlsx
│   │   │       │   ├── BOZEL 24062026.xlsx
│   │   │       │   ├── BRASFRIGO 15062026.xlsx
│   │   │       │   ├── BRASKEM 21052026.xlsx
│   │   │       │   ├── BRAVA 15052026.xlsx
│   │   │       │   ├── BRF RATING 01122025.xlsx
│   │   │       │   ├── BUNGE 18062026.xlsx
│   │   │       │   ├── C. VALE 25052026.xlsx
│   │   │       │   ├── CAMPO BELO G1 CARLOS CALDEIRA 30072026.xlsx
│   │   │       │   ├── CARGILL 11062026 - REVISÃO.xlsx
│   │   │       │   ├── CBA 24062026.xlsx
│   │   │       │   ├── CELETRO 08072026.xlsx
│   │   │       │   ├── CERMISSOES 17082026.xlsx
│   │   │       │   ├── CERTAJA 12082026.xlsx
│   │   │       │   ├── CERTHIL 17082026.xlsx
│   │   │       │   ├── CJ DO BRASIL 01072026.xlsx
│   │   │       │   ├── CLUBE CURITIBANO 06052026.xlsx
│   │   │       │   ├── COCAMAR 27-04-2026.xlsx
│   │   │       │   ├── COFCO 21072026.xlsx
│   │   │       │   ├── COOPERALFA 27052026.xlsx
│   │   │       │   ├── COOPERATIVA REGIONAL AURIVERDE RATING 12032026.xlsx
│   │   │       │   ├── COOPERLUZ 14082026.xlsx
│   │   │       │   ├── COOPERVAL 14072026.xlsx
│   │   │       │   ├── COPACOL 19082026.xlsx
│   │   │       │   ├── COPREL 18082026.xlsx
│   │   │       │   ├── CP KELKO RATING 02022026.xlsx
│   │   │       │   ├── CPTM 25062026.xlsx
│   │   │       │   ├── CSN 19062026.xlsx
│   │   │       │   ├── DANGLASS 29062026.xlsx
│   │   │       │   ├── DAUS ALIMENTOS RATING 16032026.xlsx
│   │   │       │   ├── DEXCO 22062026.xlsx
│   │   │       │   ├── DIP FRANGOS 28042026.xlsx
│   │   │       │   ├── DUPATRI HOSPITALAR.xlsx
│   │   │       │   ├── ECOURBIS - 17062026.xlsx
│   │   │       │   ├── ELEKEIROZ 19082026.xlsx
│   │   │       │   ├── ELFA MEDICAMENTOS 22052026.xlsx
│   │   │       │   ├── EMBASA 18062026.xlsx
│   │   │       │   ├── EMBRAER 05052026.xlsx
│   │   │       │   ├── EVONIK 29052026.xlsx
│   │   │       │   ├── EXTRUSAICK 17062026.xlsx
│   │   │       │   ├── FERBASA 28052026.xlsx
│   │   │       │   ├── FICHA CONSUMIDORES V1 (2)_VALE_PREENCHIDA 3.xlsx
│   │   │       │   ├── FICHA_CONSUMIDORES_AMSTED_MAXXION_PREENCHIDA.xlsx
│   │   │       │   ├── FICHA_CONSUMIDORES_CORSAN_PREENCHIDA.xlsx
│   │   │       │   ├── FICHA_CONSUMIDORES_FS_BIOENERGIA_CORRIGIDA_PCF.xlsx
│   │   │       │   ├── FICHA_CONSUMIDORES_GV_DO_BRASIL_FINAL.xlsx
│   │   │       │   ├── FICHA_CONSUMIDORES_MILI_SA_PREENCHIDA.xlsx
│   │   │       │   ├── FICHA_CONSUMIDORES_UNIMED_SOROCABA_PREENCHIDA 2.xlsx
│   │   │       │   ├── GERDAU ACOS LONGOS - 00482085.xlsx
│   │   │       │   ├── GTFOODS 15072026.xlsx
│   │   │       │   ├── HAVAN SA 06042026.xlsx
│   │   │       │   ├── HOSPITAL EVANLEGICO DE LONDRINA 20072026.xlsx
│   │   │       │   ├── INDEMIL RATING 23032026 - Copia.xlsx
│   │   │       │   ├── INDUPA 19052026.xlsx
│   │   │       │   ├── INTERCEMENT RATING 19032026.xlsx
│   │   │       │   ├── ITAMBE CIMENTOS 24072026.xlsx
│   │   │       │   ├── JBS 13052026.xlsx
│   │   │       │   ├── KINROSS 28102025.xlsx
│   │   │       │   ├── KLABIN 15052026.xlsx
│   │   │       │   ├── LDC MATRIZ.xlsx
│   │   │       │   ├── LDC SUCOS 06052026.xlsx
│   │   │       │   ├── LINHA 4 - MOTIVA 06072026.xlsx
│   │   │       │   ├── LINHAS 5 E 17 06072026.xlsx
│   │   │       │   ├── LINHAS 8 E 9 07072026.xlsx
│   │   │       │   ├── MAHLE 13082026.xlsx
│   │   │       │   ├── MARINGA FERRO LIGA 18062026.xlsx
│   │   │       │   ├── MESSER GASES 22072026.xlsx
│   │   │       │   ├── METALBRAZING 11062026.xlsx
│   │   │       │   ├── METRO SP 23062026.xlsx
│   │   │       │   ├── MINERACAO ONCA PUMA 17082026.xlsx
│   │   │       │   ├── MINERACAO RIO DO NORTE 16062026.xlsx
│   │   │       │   ├── MINERACAO USMINAS 13082026.xlsx
│   │   │       │   ├── MOTIVA SA 13082026.xlsx
│   │   │       │   ├── NADIR FIGUEIREDO 02042026.xlsx
│   │   │       │   ├── NEXA RECURSOS MINERAIS 18062026.xlsx
│   │   │       │   ├── NORFIL SA 27042026.xlsx
│   │   │       │   ├── NOVA FIAÇAO 14052026.xlsx
│   │   │       │   ├── NOVELIS 05062026.xlsx
│   │   │       │   ├── OXITENO 24062026.xlsx
│   │   │       │   ├── PARAGOMINAS 03082026.xlsx
│   │   │       │   ├── PARANA BOI 24042026.xlsx
│   │   │       │   ├── PEROXIDOS 28-04-2026.xlsx
│   │   │       │   ├── PETRORECONCAVO 08052026.xlsx
│   │   │       │   ├── PLASTICOS AMSTERDAN 13072026.xlsx
│   │   │       │   ├── PRATI DONADUZI 14072026.xlsx
│   │   │       │   ├── RANDON 03082026.xlsx
│   │   │       │   ├── REFINARIA MATARIPE 17082026.xlsx
│   │   │       │   ├── RHODIA BRASIL 20072026.xlsx
│   │   │       │   ├── RIMA INDUSTRIAL RATING 04112025.xlsx
│   │   │       │   ├── RVTRANS 31072026.xlsx
│   │   │       │   ├── SABESP 23062026.xlsx
│   │   │       │   ├── SALOBO METAIS 20082026.xlsx
│   │   │       │   ├── SAMARCO 21082026.xlsx
│   │   │       │   ├── SANEPAR 21052026.xlsx
│   │   │       │   ├── SAO MARTINHO 01062026.xlsx
│   │   │       │   ├── SCALA DATA CENTERS 0508226.xlsx
│   │   │       │   ├── SCHULZ 18082026.xlsx
│   │   │       │   ├── SERLONAS RATING 10032026.xlsx
│   │   │       │   ├── SERVENG CIVILSAN 18082026.xlsx
│   │   │       │   ├── SINOBRAS 09072026.xlsx
│   │   │       │   ├── SOUTH32 18082026.xlsx
│   │   │       │   ├── TCP RATING 04112025.xlsx
│   │   │       │   ├── TEREOS ACUCAR 14072026.xlsx
│   │   │       │   ├── TEREOS AMIDOS E ADOCANTES RATING 27112025.xlsx
│   │   │       │   ├── TERNIUM 26052026.xlsx
│   │   │       │   ├── TES Terminal Exp Santos 05052026.xlsx
│   │   │       │   ├── TRANSPETRO 08062026.xlsx
│   │   │       │   ├── TRANSPPASS 03082026.xlsx
│   │   │       │   ├── UNIAO OESTE 20052026.xlsx
│   │   │       │   ├── UNIDAS SUL 180052026.xlsx
│   │   │       │   ├── UNIMED 15072026.xlsx
│   │   │       │   ├── UNIMED LONDRINA.xlsx
│   │   │       │   ├── UNIPAR 19052026.xlsx
│   │   │       │   ├── USIMINAS 25062026.xlsx
│   │   │       │   ├── USINA LATICIÍNIOS JUSSARA 08052026.xlsx
│   │   │       │   ├── VIDROPORTO RATING 03022026.xlsx
│   │   │       │   ├── VILLARES METALS 02072026.xlsx
│   │   │       │   ├── VOTORANTIM SA 11052026.xlsx
│   │   │       │   ├── WEG - MATRIZ 15052026.xlsx
│   │   │       │   └── WHITE MARTINS 30072026.xlsx
│   │   │       └── processados/
│   │   │           └── GERDAU AÇOS LONGOS RATING 27032026.xlsx
│   │   └── reprocessamento/
│   │       └── pendentes/
│   ├── garantias/
│   │   └── garantias.csv
│   ├── mtm/
│   │   └── data.csv
│   ├── overrides/
│   │   └── pendentes/
│   ├── receita/
│   │   └── cache/
│   │       └── receita_cache.json
│   ├── reprocessamento/
│   │   └── comercializadoras/
│   │       └── pendentes/
│   │           ├── ELETROBRAS.xlsx
│   │           ├── ELETROBRAS_24092025.xlsx
│   │           └── WD AGROINDUSTRIAL 13072026.xlsx
│   └── salesforce/
│       └── salesforce.xlsx
├── LOGS/
│   ├── atualizacoes_manuais/
│   │   └── MAN_20260910_154541__carga_manual.log
│   ├── auditoria/
│   │   ├── REC_MTM_DENODO_20260910_154554__reconciliacao.log
│   │   └── REC_SF_20260910_154554__salesforce_reconciliacao.log
│   ├── execucao/
│   │   ├── BDC_20260910_153728__fichas_comercializadoras.log
│   │   ├── BDC_20260910_154203__fichas_consumidores.log
│   │   └── cli_comercializadoras.log
│   ├── general/
│   │   └── 2026-09-10_general.log
│   ├── gold/
│   │   └── GOLD_20260910_154608__service_gold.log
│   ├── ingestao/
│   │   ├── BUR_20260910_154515__ingestao_bureau.log
│   │   ├── GAR_20260910_154536__ingestao_garantias.log
│   │   ├── MTM_20260910_154446__ingestao_mtm.log
│   │   ├── REC_20260910_154513__ingestao_receita.log
│   │   └── SF_20260910_154447__ingestao_salesforce.log
│   ├── rejeitados/
│   │   └── 2026-09-10_rejeicoes.json
│   ├── relacional/
│   │   ├── ALERT_20260910_154607__servico_alertas.log
│   │   ├── F_GAR_20260910_154544__fato_garantia.log
│   │   ├── FATO_ANL_20260910_154543__fato_analise_credito.log
│   │   ├── MAN_20260910_154607__alertas_manuais.log
│   │   └── RSK_20260910_154553__fato_risco.log
│   └── runner/
│       └── RUN_20260910_153728__orquestrador_principal.log
├── SAIDAS/
│   ├── bronze/
│   │   ├── blacklist_raw/
│   │   ├── fichas_comercializadoras_raw/
│   │   │   ├── 00001180000126__ELETROBRAS_COMER/
│   │   │   │   ├── AXIA 24082026__padrao_6__00001180000126__31122024__97d31ef6.xlsx
│   │   │   │   └── ELETROBRAS_24092025__padrao_3__00001180000126__31122024__169c22c5.xlsx
│   │   │   ├── 00001180000207__ELETROBRAS/
│   │   │   │   └── ELETROBRAS__padrao_3__00001180000207__31122024__f4f5ddb1.xlsx
│   │   │   ├── 00350763000162__JEF_CO/
│   │   │   │   └── J&F 15092025__padrao_3__00350763000162__31122024__47eee93c.xlsx
│   │   │   ├── 00350763002297__J&F_COM/
│   │   │   │   ├── J&F 20082026__padrao_6__00350763002297__31122025__33c2a665.xlsx
│   │   │   │   └── J&F DF 2024 holding__padrao_6__00350763002297__31122024__455fed23.xlsx
│   │   │   ├── 01105558000102__UTE_WD/
│   │   │   │   └── WD AGROINDUSTRIAL 13072026__padrao_6__01105558000102__31122025__5d08213f.xlsx
│   │   │   ├── 02691745000170__TRADENER/
│   │   │   │   ├── TRADENER 17052024__padrao_6__02691745000170__31122023__cfbceee6.xlsx
│   │   │   │   ├── TRADENER 29_08_2022__padrao_2__02691745000170__31122021__6b4614b1.xlsx
│   │   │   │   ├── TRADENER_02_09_2021__padrao_2__02691745000170__31122020__3c15126f.xlsx
│   │   │   │   ├── TRADENER_10042025__padrao_3__02691745000170__31122024__b5c7c6ef.xlsx
│   │   │   │   └── Tradener_15092023 - Copia__padrao_3__02691745000170__31122022__a45b0d14.xlsx
│   │   │   ├── 02916265037837__JBS_COM_PR/
│   │   │   │   └── JBS_08.07.2024__padrao_3__02916265037837__31122023__d8ce4880.xlsx
│   │   │   ├── 02998301000181__RIO_PARANAPAN/
│   │   │   │   └── RIO PARANAPANEMA 13042026__padrao_6__02998301000181__31122024__91d0d374.xlsx
│   │   │   ├── 03358698000100__SUNITY/
│   │   │   │   └── SUDOESTE ENERGIA 14_06_2022__padrao_2__03358698000100__31122021__3dd503c6.xlsx
│   │   │   ├── 03538572000117__PBEN-P/
│   │   │   │   └── PBEN_12.06.2024__padrao_3__03538572000117__31122023__f858139b.xlsx
│   │   │   ├── 03631957000124__CTG_TRADING/
│   │   │   │   ├── CTG Trading_04_06_2021__padrao_2__03631957000124__31122020__c9586425.xlsx
│   │   │   │   ├── CTG Trading_16082023__padrao_3__03631957000124__31122022__fa6ef875.xlsx
│   │   │   │   └── CTG trading_28.08.2024__padrao_3__03631957000124__31122023__d727535f.xlsx
│   │   │   ├── 03780401000108__BROOKFIELDC/
│   │   │   │   ├── BROOKFIELD_01_09_2021__padrao_2__03780401000108__31122020__dcc16cbc.xlsx
│   │   │   │   └── BROOKFILD 04_05_2022__padrao_2__03780401000108__31122021__66817274.xlsx
│   │   │   ├── 03780401000108__ELERAC/
│   │   │   │   ├── ELERA COM 31072025__padrao_3__03780401000108__31122024__6a6127b8.xlsx
│   │   │   │   ├── ELERA_19012024__padrao_3__03780401000108__31122022__74a614b1.xlsx
│   │   │   │   └── ELERA_30.07.2024__padrao_3__03780401000108__31122023__f7891b81.xlsx
│   │   │   ├── 03926572000194__ITAMBE/
│   │   │   │   └── ITAMBE ENERGETICA 29072026__padrao_6__03926572000194__31122025__be0aeebe.xlsx
│   │   │   ├── 03953509000147__CPFL_GERACAO/
│   │   │   │   └── CELESC 11_05_2022__padrao_2__03953509000147__31122021__394a24ec.xlsx
│   │   │   ├── 03984862000194__AUREN/
│   │   │   │   ├── AUREN COM 22072026__padrao_6__03984862000194__31122025__3d576fdf.xlsx
│   │   │   │   ├── AUREN_13.06.2024__padrao_3__03984862000194__31122023__e5bf103e.xlsx
│   │   │   │   ├── AUREN_16062023__padrao_3__03984862000194__31122022__9239e50f.xlsx
│   │   │   │   └── AUREN_24092025__padrao_3__03984862000194__18032025__ad0be7ac.xlsx
│   │   │   ├── 03984862000194__VOTENER/
│   │   │   │   └── VOTENER_09_06_2021__padrao_2__03984862000194__31122020__7a3234d8.xlsx
│   │   │   ├── 04023261000188__NC_ENERGIA/
│   │   │   │   ├── FICHA MODELO_xx.xx.2025_1.0__padrao_3__04023261000188__31122023__8886fe30.xlsx
│   │   │   │   ├── NC_30.07.2024__padrao_3__04023261000188__31122023__546df139.xlsx
│   │   │   │   ├── NEO ENERGIA 01102025__padrao_3__04023261000188__25032025__b15c69f1.xlsx
│   │   │   │   ├── Neoenergia 25082023__padrao_3__04023261000188__31122022__61fbc8a1.xlsx
│   │   │   │   └── NEOENERGIA RATING 24032026__padrao_6__04023261000188__31122024__0363dafb.xlsx
│   │   │   ├── 04029601000188__ENERGEST/
│   │   │   │   └── ENERGEST 17082026__padrao_6__04029601000188__31122025__d6c4b48e.xlsx
│   │   │   ├── 04100556000100__ENGIE_BR_COM/
│   │   │   │   ├── ENGIE 01072025__padrao_3__04100556000100__31122024__bbd16987.xlsx
│   │   │   │   ├── ENGIE 12052026__padrao_6__04100556000100__31122025__e8ed31fe.xlsx
│   │   │   │   ├── Engie_31082023__padrao_3__04100556000100__31122022__1597818f.xlsx
│   │   │   │   └── ENGIECOM_06.06.2024__padrao_3__04100556000100__31122023__c0b8a668.xlsx
│   │   │   ├── 04149295000113__EDP_C/
│   │   │   │   ├── CELESC_16042024__padrao_3__04149295000113__31122023__f55e254f.xlsx
│   │   │   │   ├── EDP 21052026__padrao_6__04149295000113__31122025__772dd5a8.xlsx
│   │   │   │   ├── EDP_12062023__padrao_3__04149295000113__31122022__3fd84da0.xlsx
│   │   │   │   └── EDP_2025__padrao_3__04149295000113__31122024__b45c24de.xlsx
│   │   │   ├── 04270778000171__SANTANDER_COM/
│   │   │   │   ├── SANTADER_26.06.2024__padrao_3__04270778000171__31122023__dfd9038a.xlsx
│   │   │   │   ├── Santander 13062023__padrao_3__04270778000171__31122022__7af15b0c.xlsx
│   │   │   │   └── SANTANDER RATING 24102025__padrao_7__04270778000171__31122024__f7c82a17.xlsx
│   │   │   ├── 04370282000170__COPEL_GET/
│   │   │   │   └── COPELGET_27112024__padrao_3__04370282000170__31122023__4b9379fb.xlsx
│   │   │   ├── 04423567000121__ENEVA/
│   │   │   │   ├── ENEVA 28072026__padrao_6__04423567000121__31122025__9b2a45e2.xlsx
│   │   │   │   ├── ENEVA 30102025__padrao_7__04423567000121__31122024__9c316a99.xlsx
│   │   │   │   └── ENEVA_29.05.2024__padrao_3__04423567000121__31122023__aa25fd1d.xlsx
│   │   │   ├── 04426411000102__ENERPEIXE/
│   │   │   │   ├── ENERPEIXE 20082026__padrao_6__04426411000102__31122025__14cea463.xlsx
│   │   │   │   └── ENERPEIXE COMERCIALIZADORA16092025__padrao_3__04426411000102__31122024__d4e76877.xlsx
│   │   │   ├── 04462976000137__IBS-ENERGY/
│   │   │   │   ├── IBS 13_06_2022__padrao_2__04462976000137__31122021__d792521d.xlsx
│   │   │   │   ├── IBS Energy_04082023__padrao_3__04462976000137__31122022__bd7fe3e2.xlsx
│   │   │   │   ├── IBS_09_09_2021__padrao_2__04462976000137__31122020__7024276d.xlsx
│   │   │   │   └── IBS_24_06_2024__padrao_6__04462976000137__31122023__884ef836.xlsx
│   │   │   ├── 04518259000180__ELECTRA_ENERGY/
│   │   │   │   ├── ELECTRA 26032024__padrao_3__04518259000180__30062023__4ff8c117.xlsx
│   │   │   │   ├── ELECTRA 29_08_2022__padrao_2__04518259000180__31122021__0e2c4687.xlsx
│   │   │   │   ├── ELECTRA ENERGY 18_04_2023__padrao_3__04518259000180__31122022__c07f212e.xlsx
│   │   │   │   ├── ELECTRA ENERGY_2024__padrao_3__04518259000180__31122024__bd4943f3.xlsx
│   │   │   │   ├── ELECTRA_02_09_2021__padrao_2__04518259000180__31122020__29638a1c.xlsx
│   │   │   │   └── ELECTRA_15042024__padrao_3__04518259000180__31122023__a6daf950.xlsx
│   │   │   ├── 04591168000170__FOZ_DO_CHAPECO/
│   │   │   │   └── Foz do Chapeco 05082026__padrao_6__04591168000170__31122025__23f7d636.xlsx
│   │   │   ├── 04755710000182__POLLARIX/
│   │   │   │   └── POLLARIX 03062026__padrao_6__04755710000182__31122025__10fd5d33.xlsx
│   │   │   ├── 04802543000183__DELTA_ENERGIA/
│   │   │   │   ├── DELTA 12_04_2022 31 12 2021__padrao_2__04802543000183__31122020__e2ea8941.xlsx
│   │   │   │   └── DELTA_19022025__padrao_3__04802543000183__31122023__8bba3871.xlsx
│   │   │   ├── 04810290000190__PIE_-_RP/
│   │   │   │   └── PIE RP 17_11_2022__padrao_2__04810290000190__31122021__f472e843.xlsx
│   │   │   ├── 04973790000142__CPFL_BRASIL/
│   │   │   │   ├── CPFL 04072025__1__padrao_3__04973790000142__31122024__c60754b4.xlsx
│   │   │   │   ├── CPFL 06082026__padrao_6__04973790000142__22012026__9d30dc0c.xlsx
│   │   │   │   ├── CPFL_11.08.2023___padrao_3__04973790000142__31122022__b061dcba.xlsx
│   │   │   │   └── CPFL_28.08.2024__padrao_3__04973790000142__31122023__c8829980.xlsx
│   │   │   ├── 05263973000137__CEMIG_TRADING/
│   │   │   │   └── CEMIG 05-07-2024 trading__padrao_3__05263973000137__31122023__e24e2119.xlsx
│   │   │   ├── 05350372000161__PCHAQUARIUS/
│   │   │   │   └── AQUARIUS 11062026__padrao_6__05350372000161__31122025__24dd195b.xlsx
│   │   │   ├── 05352237000155__ECOM/
│   │   │   │   ├── ECOM 17_05_2022__padrao_2__05352237000155__31122021__3476990c.xlsx
│   │   │   │   ├── ECOM 22042026__padrao_6__05352237000155__31122025__2c05bea0.xlsx
│   │   │   │   ├── ECOM 23112023__padrao_6__05352237000155__31122022__8d44f2fe.xlsx
│   │   │   │   ├── ECOM 27032026__padrao_6__05352237000155__31122024__4c9e4ba9.xlsx
│   │   │   │   ├── ECOM_11042024__padrao_3__05352237000155__31122023__b0f37e54.xlsx
│   │   │   │   ├── ECOM_14_10_2021__padrao_2__05352237000155__31122020__f20d442d.xlsx
│   │   │   │   └── ECOM_2024__padrao_3__05352237000155__31122024__d2ac0d64.xlsx
│   │   │   ├── 05449127000106__BRF_COM/
│   │   │   │   └── BRF Energia 15072025__padrao_3__05449127000106__31122024__0948b34a.xlsx
│   │   │   ├── 05938884000143__UTE_VALE_DO_PARANA/
│   │   │   │   └── UTE VALE DO PARANA__padrao_6__05938884000143__31122025__598255a0.xlsx
│   │   │   ├── 07131859000189__BRADESCO_ENERGIA/
│   │   │   │   ├── BRADESCO 04072025__padrao_3__07131859000189__17122024__b5b99522.xlsx
│   │   │   │   └── BRADESCO 30072026__padrao_6__07131859000189__31122025__be94bc7b.xlsx
│   │   │   ├── 07133522000100__BTG_PACTUAL/
│   │   │   │   └── BTG 15102025__padrao_3__07133522000100__31122024__e7ed4dfc.xlsx
│   │   │   ├── 07358761000169__GALB/
│   │   │   │   ├── GERDAU AÇOS LONGOS 23 04 2024__padrao_3__07358761000169__31122023__374624fd.xlsx
│   │   │   │   └── Gerdau Aços Longos_20_09_2021__padrao_2__07358761000169__31122020__00abd54d.xlsx
│   │   │   ├── 07393256000155__DIFERENCIAL/
│   │   │   │   ├── DIFERENCIAL 13_04_2022__padrao_2__07393256000155__31122021__c8314860.xlsx
│   │   │   │   ├── DIFERENCIAL_02_09_2021__padrao_2__07393256000155__31122020__fe547de6.xlsx
│   │   │   │   ├── DIFERENCIAL_16.05.2024__padrao_3__07393256000155__31122023__baf2fadb.xlsx
│   │   │   │   └── DIFERENCIAL_20072023__padrao_3__07393256000155__31122022__46536b7a.xlsx
│   │   │   ├── 07416174000189__BR_ENERGIAS/
│   │   │   │   └── BR ENERGIAS RATING 03022026__padrao_6__07416174000189__31122024__5d8e716a.xlsx
│   │   │   ├── 07685694000197__ENERGISA_COM/
│   │   │   │   ├── ENERGISA 07052024__padrao_3__07685694000197__31122023__3e786d54.xlsx
│   │   │   │   ├── ENERGISA 08052026__padrao_6__07685694000197__31122025__1bebb2db.xlsx
│   │   │   │   └── ENERGISA 30102025__padrao_7__07685694000197__31122024__dacbf519.xlsx
│   │   │   ├── 07725608000122__LUDFOR_ENERGIA/
│   │   │   │   └── LUDFOR_09_09_2021__padrao_2__07725608000122__31122020__94477d4f.xlsx
│   │   │   ├── 07760179000124__FOCUS/
│   │   │   │   └── FOCUS ENERGIA _07_05_2021__padrao_2__07760179000124__31122020__e3afbdf5.xlsx
│   │   │   ├── 07794616000120__CZARNIKOW/
│   │   │   │   ├── CZARNIKOW 09062026__padrao_6__07794616000120__31122025__46500a1c.xlsx
│   │   │   │   ├── CZARNIKOW 13062025__padrao_3__07794616000120__31122024__4bb069a4.xlsx
│   │   │   │   ├── Czarnikow 27-01-2025__padrao_3__07794616000120__31122023__2cf2e811.xlsx
│   │   │   │   ├── CZARNIKOW 27032026__padrao_6__07794616000120__31122024__c6d78952.xlsx
│   │   │   │   ├── CZARNIKOW 27_09_2022__padrao_2__07794616000120__31122021__4276080a.xlsx
│   │   │   │   └── CZARNIKOW_07_06_2021 (zerada manualmente__padrao_2__07794616000120__31122020__177ea59e.xlsx
│   │   │   ├── 07823304000106__IJUI/
│   │   │   │   ├── IJUÍ 02072026__padrao_6__07823304000106__31122025__f86364cf.xlsx
│   │   │   │   └── IJUÍ 13072026__padrao_6__07823304000106__31122025__1dbd3b76.xlsx
│   │   │   ├── 07829836000142__CHAPECOENSE_GERAÇÃO_S.A_E_CONTROLADA/
│   │   │   │   └── FOZ DO CHAPECO RATING 27012026__padrao_6__07829836000142__31122024__0852ea15.xlsx
│   │   │   ├── 07966116000129__UTE_CODORA/
│   │   │   │   └── ALBIOMA CODORA__padrao_6__07966116000129__31122025__9c3a6d7a.xlsx
│   │   │   ├── 08032643000129__MARACANA_ENERG/
│   │   │   │   └── MARACANA 06082026__padrao_6__08032643000129__31122025__859dee94.xlsx
│   │   │   ├── 08032643000129__MARACANA_ENERGETICA/
│   │   │   │   └── MARACANÃ ENERGÉTICA RATING 22012026__padrao_6__08032643000129__31122024__cedbcca7.xlsx
│   │   │   ├── 08070508000178__ATVOS_PART/
│   │   │   │   └── ATVOS PART. 03082026__padrao_6__08070508000178__31032026__fdee3e1e.xlsx
│   │   │   ├── 08070566000100__BRENCO/
│   │   │   │   └── ATVOS BRENCO 27072026__padrao_6__08070566000100__31032026__196c81e6.xlsx
│   │   │   ├── 08323274000123__COPREL_GERACAO/
│   │   │   │   └── COPREL GERAÇÃO 23062026__padrao_6__08323274000123__31122025__fc3e160e.xlsx
│   │   │   ├── 08336804000178__CELESC_GERA/
│   │   │   │   └── CELESC Geração 28052026__padrao_6__08336804000178__31122025__0076c014.xlsx
│   │   │   ├── 08364948000138__ALUPAR/
│   │   │   │   ├── ALUPAR 19112024__padrao_3__08364948000138__31122023__10a891eb.xlsx
│   │   │   │   └── ALUPAR_06062025__padrao_3__08364948000138__31122024__d0cfa612.xlsx
│   │   │   ├── 08439659000150__CPFL_RENOVAVEIS/
│   │   │   │   └── CPFL 04072025__padrao_3__08439659000150__31122024__5d728606.xlsx
│   │   │   ├── 08573833000153__STATKRAFT/
│   │   │   │   ├── STAKRAFT_05.07.2024__padrao_3__08573833000153__31122023__d39b0e2c.xlsx
│   │   │   │   └── STATKRAFT 27082025__padrao_3__08573833000153__31122024__61a05183.xlsx
│   │   │   ├── 08578334000159__FIBRAENERGY/
│   │   │   │   ├── FIBRA 06082026__padrao_6__08578334000159__31122025__484f0112.xlsx
│   │   │   │   ├── Fibra Energy 14052025__padrao_3__08578334000159__31122024__a982b556.xlsx
│   │   │   │   └── FIBRA_GRUPO 24062025__padrao_3__08578334000159__31122024__2cd524ae.xlsx
│   │   │   ├── 08598391000108__URC/
│   │   │   │   └── ATVOS RIO CLARO 31072026__padrao_6__08598391000108__31032026__3f8bbb51.xlsx
│   │   │   ├── 08666285000106__QAIR_BRASIL_PARTICIPACOES_S.A/
│   │   │   │   └── QAIR 01042026__padrao_6__08666285000106__31122024__f04e04fb.xlsx
│   │   │   ├── 08773135000100__2WENERGIA/
│   │   │   │   ├── 2W ENERGIA 05_07_2022__padrao_2__08773135000100__31122021__3caa8318.xlsx
│   │   │   │   ├── 2W ENERGIA_28.08.2024__padrao_3__08773135000100__30092023__c1d3e2e9.xlsx
│   │   │   │   ├── 2W_13062023 - Copia__padrao_6__08773135000100__31122022__5ffd71f6.xlsx
│   │   │   │   └── 2W_18_06_2021__padrao_2__08773135000100__31122020__945043a6.xlsx
│   │   │   ├── 08793343000162__BEVAP/
│   │   │   │   ├── BEVAP 11082026__padrao_6__08793343000162__31032026__3b69096f.xlsx
│   │   │   │   └── BEVAP SA RATING 03032026__padrao_6__08793343000162__31032025__93905d3c.xlsx
│   │   │   ├── 08793343000162__PARACATU/
│   │   │   │   └── PARACATU RATING 26022026__padrao_6__08793343000162__31032025__6c4f5db3.xlsx
│   │   │   ├── 08842785000151__APTCOM/
│   │   │   │   ├── APOLO 02_05_2022__padrao_2__08842785000151__31122021__b9a6f52a.xlsx
│   │   │   │   └── APOLO_24_06_2021__padrao_2__08842785000151__31122020__bfaead97.xlsx
│   │   │   ├── 09020211000160__PCH_LAJARI/
│   │   │   │   ├── FICHA_GERADORAS_LAJARI_PASSO4__padrao_6__09020211000160__31122025__818c2dd7.xlsx
│   │   │   │   └── LAJARI ENERGETICA RATING 26012026__padrao_6__09020211000160__31122024__56c418e5.xlsx
│   │   │   ├── 09149503000106__OMG/
│   │   │   │   ├── OMG_07062023__padrao_3__09149503000106__31122022__5873e3ec.xlsx
│   │   │   │   └── SERENA 18 04 2024__padrao_3__09149503000106__31122023__96b60b14.xlsx
│   │   │   ├── 09149503000106__SERENA/
│   │   │   │   └── SERENA 15072025__padrao_3__09149503000106__31122024__d17afe85.xlsx
│   │   │   ├── 09185485000100__ENEVA_COM/
│   │   │   │   └── ENEVA_29.05.2024__1__padrao_3__09185485000100__31122023__e654b06c.xlsx
│   │   │   ├── 09222477000196__RAHCROL/
│   │   │   │   └── RAHCROL_10_09_2021__padrao_2__09222477000196__31122019__aede84c6.xlsx
│   │   │   ├── 09495582000107__SAFIRA_COM/
│   │   │   │   ├── SAFIRA 11042024__padrao_6__09495582000107__31122023__3ff90bd0.xlsx
│   │   │   │   ├── SAFIRA 27032026 DF 2024__padrao_6__09495582000107__31122024__ed3c1dfe.xlsx
│   │   │   │   ├── SAFIRA ADM__padrao_3__09495582000107__31122024__1492d833.xlsx
│   │   │   │   ├── SAFIRA COM_05_03_2021__padrao_2__09495582000107__31122020__49134c2e.xlsx
│   │   │   │   ├── SAFIRA_12_05_2022__padrao_2__09495582000107__31122021__08338d1f.xlsx
│   │   │   │   └── SAFIRA_27042023__padrao_3__09495582000107__31122022__99f0776a.xlsx
│   │   │   ├── 09625739000163__GERAMAMORE/
│   │   │   │   ├── GERAMAMORE 27082025__padrao_3__09625739000163__31122024__64365582.xlsx
│   │   │   │   ├── GERAMAMORE_06.06.2024__padrao_3__09625739000163__31122023__4a38d113.xlsx
│   │   │   │   ├── GERAMAMORÉ 30112023__padrao_3__09625739000163__31122022__1132222a.xlsx
│   │   │   │   ├── GERAMAMORÉ RATING 00359795__padrao_6__09625739000163__31122024__8406352e.xlsx
│   │   │   │   ├── GERAMAMORÉ_28_10_2021__padrao_2__09625739000163__31122020__4e5d9369.xlsx
│   │   │   │   └── SGS Brasil 19-01-2023__padrao_3__09625739000163__31122021__b572d7cc.xlsx
│   │   │   ├── 10202852000115__KROMA/
│   │   │   │   ├── KROMA 17112023__padrao_6__10202852000115__31122022__833b4375.xlsx
│   │   │   │   ├── KROMA 31_05_2022__padrao_2__10202852000115__31122021__ea2489e8.xlsx
│   │   │   │   └── KROMA_24_05_2021__padrao_2__10202852000115__31122020__2efa29b2.xlsx
│   │   │   ├── 10466806000123__SPOT_ENERGIA/
│   │   │   │   └── SPOT_12.06.2024__padrao_6__10466806000123__31122023__f17c9baf.xlsx
│   │   │   ├── 10671322000116__DEAL_COMERCIALIZADORA/
│   │   │   │   ├── DEAL 10_05_2022__padrao_2__10671322000116__31122021__da502dae.xlsx
│   │   │   │   ├── DEAL 16102025__padrao_3__10671322000116__31122024__4def4933.xlsx
│   │   │   │   ├── DEAL 27102023__padrao_3__10671322000116__31122022__b7d51c48.xlsx
│   │   │   │   ├── DEAL 29062026__padrao_6__10671322000116__31122025__c9817d83.xlsx
│   │   │   │   ├── DEAL RATING 16102025__padrao_6__10671322000116__31122024__14abab02.xlsx
│   │   │   │   ├── DEAL_14_10_2021__padrao_2__10671322000116__31122020__6402fbfb.xlsx
│   │   │   │   └── DEAL_26.06.2024__padrao_6__10671322000116__31122023__62098ec6.xlsx
│   │   │   ├── 10763227000142__UTE_SANTA_CRUZ/
│   │   │   │   └── BIOENERGETICA SANTA CRUZ RATING 02022026__padrao_6__10763227000142__31122024__86cc5b94.xlsx
│   │   │   ├── 11017349000152__LEROS_ENERGIA/
│   │   │   │   └── LÉROS_10_09_2021__padrao_2__11017349000152__31122020__b05417da.xlsx
│   │   │   ├── 11040403000180__RIALMA_V/
│   │   │   │   └── RIALMA V 06072026__padrao_6__11040403000180__31122025__b72fcdc8.xlsx
│   │   │   ├── 11085823000183__AMERICA/
│   │   │   │   ├── AMERICA_07_06_2021__padrao_2__11085823000183__31122020__7e6a0991.xlsx
│   │   │   │   └── AMERICA_20.05.2024__padrao_6__11085823000183__31122023__49703718.xlsx
│   │   │   ├── 11182210000164__NOVA_ENERGIA/
│   │   │   │   ├── NOVA 25 04 2024__padrao_6__11182210000164__31122023__e0eb18da.xlsx
│   │   │   │   ├── NOVA ENERGIA 08_06_2022__padrao_2__11182210000164__31122021__b96ea78a.xlsx
│   │   │   │   ├── Nova Energia_16_06_2021__padrao_2__11182210000164__31122020__22334954.xlsx
│   │   │   │   └── NOVA_ENERGIA2024__padrao_6__11182210000164__31122024__21316198.xlsx
│   │   │   ├── 11251784000147__GAMA/
│   │   │   │   └── GAMA_06_09_2021__padrao_2__11251784000147__31122020__69638f8f.xlsx
│   │   │   ├── 11315117000180__LIGHTCOM/
│   │   │   │   ├── LIGHT 18 04 2024__padrao_3__11315117000180__31122023__f64d0fc2.xlsx
│   │   │   │   ├── LIGHT COM  RATING 22122025__padrao_6__11315117000180__31122024__a0b7ecaa.xlsx
│   │   │   │   ├── LIGHT COM 07052026__padrao_6__11315117000180__31122025__3d8d442c.xlsx
│   │   │   │   ├── LIGHT_10_09_2021__padrao_2__11315117000180__31122020__7fdf3f55.xlsx
│   │   │   │   └── LIGHT_2024__padrao_3__11315117000180__31122024__7d930785.xlsx
│   │   │   ├── 11316814000156__RCESA/
│   │   │   │   └── Rio Canoas (CTG) 17042026__padrao_6__11316814000156__31122024__f2bfaa57.xlsx
│   │   │   ├── 11322550000143__ATMO/
│   │   │   │   ├── ATMO 04052026__padrao_6__11322550000143__31122025__375dcb8b.xlsx
│   │   │   │   ├── ATMO 06_05_2022__padrao_2__11322550000143__31122021__2f8d89de.xlsx
│   │   │   │   ├── ATMO 16052025__1__padrao_3__11322550000143__31122024__c3b57c83.xlsx
│   │   │   │   ├── ATMO 27032026__padrao_6__11322550000143__31122024__e6d41510.xlsx
│   │   │   │   ├── ATMO_06.06.2024__padrao_6__11322550000143__31122023__179ccc1c.xlsx
│   │   │   │   ├── ATMO_16062023__padrao_3__11322550000143__31122022__555e4f07.xlsx
│   │   │   │   └── ATMO_31_08_2021__padrao_2__11322550000143__31122020__4f162783.xlsx
│   │   │   ├── 11322550000224__ATMO/
│   │   │   │   └── ATMO 16052025__padrao_3__11322550000224__31122024__9d3f04a9.xlsx
│   │   │   ├── 11482752000152__SAFIRA_VAREJO/
│   │   │   │   ├── SAFIRA 08_06_2022__padrao_2__11482752000152__31122021__e849f835.xlsx
│   │   │   │   ├── SAFIRA VAREJISTA_2023__padrao_3__11482752000152__31122023__1b47b800.xlsx
│   │   │   │   └── SAFIRA VAREJISTA_2024__padrao_3__11482752000152__31122024__6dcc8a81.xlsx
│   │   │   ├── 11599292000147__CAPITALE/
│   │   │   │   ├── CAPITALE 01102025__padrao_3__11599292000147__31122024__b6c7145e.xlsx
│   │   │   │   ├── CAPITALE 27032026__padrao_6__11599292000147__31122024__52069d58.xlsx
│   │   │   │   ├── CAPITALE 28052026__padrao_6__11599292000147__31122025__cea1dd9e.xlsx
│   │   │   │   ├── CAPITALE 30_05_2022__padrao_2__11599292000147__31122021__8191a942.xlsx
│   │   │   │   ├── CAPITALE_16062023__padrao_3__11599292000147__31122022__6c9f544e.xlsx
│   │   │   │   └── CAPITALE_26.06.2024__padrao_6__11599292000147__31122023__20236dcb.xlsx
│   │   │   ├── 11820864000176__IBITU_COM/
│   │   │   │   ├── IBITU 05122024 - Copia__padrao_3__11820864000176__31122023__e7963454.xlsx
│   │   │   │   ├── IBITU 06_06_2022__padrao_2__11820864000176__31122021__fc0b5a79.xlsx
│   │   │   │   └── IBITU 19062026__padrao_6__11820864000176__31122025__cbdc82ec.xlsx
│   │   │   ├── 11820864000176__QUEIROZ_GALVAO_ENERGIA/
│   │   │   │   └── IBITU RATING 11112025__padrao_7__11820864000176__31122024__b971cf7d.xlsx
│   │   │   ├── 12009135000105__ALIANCA_GERACAO/
│   │   │   │   ├── ALIANCA_GERACAO 28052026__padrao_6__12009135000105__31122025__86a7ff62.xlsx
│   │   │   │   └── ALIANÇA 20_07_2022__padrao_2__12009135000105__31122021__4bef1e0a.xlsx
│   │   │   ├── 12009135000105__ALIANCA_GERACAO_DE_ENERGIA_S.A/
│   │   │   │   └── ALIANÇA GERAÇÃO RATING 06022026__padrao_6__12009135000105__31122024__c8cace32.xlsx
│   │   │   ├── 12150746000160__SANTA_HELENA/
│   │   │   │   └── SANTA HELENA ENERGIA 15062026__padrao_6__12150746000160__31122025__c2ca5fd3.xlsx
│   │   │   ├── 12291462000194__BIOENERGÉTICA_SÃO_MARTINHO_SA/
│   │   │   │   └── BIOENERGÉTICA SÃO MARTINHO RATING 020220__padrao_6__12291462000194__31032025__9f8e2914.xlsx
│   │   │   ├── 12300288000107__NESA/
│   │   │   │   └── NORTE ENERGIA 14052026__padrao_6__12300288000107__31122025__f85081b0.xlsx
│   │   │   ├── 12368097000179__BO_ENERGY/
│   │   │   │   ├── BO ENERGY 04_05_2022__padrao_2__12368097000179__31122021__b2a4cc49.xlsx
│   │   │   │   └── BOENERGY_08052023__padrao_4__12368097000179__31122022__464ec637.xlsx
│   │   │   ├── 12422540000142__AGROENERGIA/
│   │   │   │   └── AGROENERGIA _10_05_2021__padrao_2__12422540000142__31122020__1e49e51e.xlsx
│   │   │   ├── 12458962000178__ENEX/
│   │   │   │   └── ENEX_17_06_2021__padrao_2__12458962000178__31122020__f4452e93.xlsx
│   │   │   ├── 12630054000110__MAXIMA_ENERGIA/
│   │   │   │   ├── MAXIMA 01_02_2023__padrao_2__12630054000110__31122021__f8498528.xlsx
│   │   │   │   ├── Maxima 21112023__padrao_3__12630054000110__31122022__cade6e01.xlsx
│   │   │   │   ├── MAXIMA_18_06_2021__padrao_2__12630054000110__31122020__e92e46ab.xlsx
│   │   │   │   └── MAXIMA_21.05.2024__padrao_6__12630054000110__31122023__c106e40a.xlsx
│   │   │   ├── 12809025000110__PRIME_ENERGY/
│   │   │   │   ├── PRIME ENERGY 02_08_2022__padrao_2__12809025000110__31122021__772478b8.xlsx
│   │   │   │   ├── PRIME ENERGY _21_06_2021__padrao_2__12809025000110__31122020__74a55640.xlsx
│   │   │   │   ├── PRIME_12.07.2024__padrao_6__12809025000110__31122023__113162fb.xlsx
│   │   │   │   └── PRIME_16.06.2023__padrao_3__12809025000110__31122022__ff583239.xlsx
│   │   │   ├── 13145928000106__BRASIL_COM/
│   │   │   │   ├── BRASIL COM 11_07_2022__padrao_2__13145928000106__31122021__4a9020dc.xlsx
│   │   │   │   ├── BRASIL COM_11_06_2021__padrao_2__13145928000106__31122020__68d80f92.xlsx
│   │   │   │   └── BRASIL COM_18_04_2023__padrao_3__13145928000106__31122022__0d0d6eee.xlsx
│   │   │   ├── 13338734000127__RBE_ENERGIA/
│   │   │   │   ├── RBE 01072025__padrao_3__13338734000127__31122024__d984855c.xlsx
│   │   │   │   ├── RBE 15_06_2022__padrao_2__13338734000127__31122021__e6f689af.xlsx
│   │   │   │   ├── RBE 31102023__padrao_6__13338734000127__31122022__e1121fdf.xlsx
│   │   │   │   └── RBE_05.06.2024__padrao_3__13338734000127__31122023__b9c0c665.xlsx
│   │   │   ├── 13459301000120__SOLENERGIAS/
│   │   │   │   ├── SOLENERGIAS 06_06_2022__padrao_2__13459301000120__31122021__90b51a69.xlsx
│   │   │   │   └── SOLENERGIAS_05.06.2024__padrao_3__13459301000120__31122023__97bdfedf.xlsx
│   │   │   ├── 13700609000115__BOLT/
│   │   │   │   ├── BOLT 05092023__padrao_3__13700609000115__31122022__a7525c59.xlsx
│   │   │   │   ├── BOLT 06_06_2022__padrao_2__13700609000115__31122021__348e71d5.xlsx
│   │   │   │   ├── BOLT_01_09_2021__padrao_2__13700609000115__31122020__2eb1e752.xlsx
│   │   │   │   ├── BOLT_17.05.2024__padrao_3__13700609000115__31122023__d8044fcc.xlsx
│   │   │   │   └── BOLT_2024__padrao_3__13700609000115__31122024__09f8e4b2.xlsx
│   │   │   ├── 13777004000122__WXE/
│   │   │   │   ├── WX ENERGIA(RAIZEN)_04.07.2024__padrao_3__13777004000122__31122023__2ad8e513.xlsx
│   │   │   │   ├── WX ENERGY_10_09_2021__padrao_2__13777004000122__31032020__cf9a5a92.xlsx
│   │   │   │   └── WXE - RAÍZEN 25082023__padrao_3__13777004000122__31122022__2872b114.xlsx
│   │   │   ├── 14023604000168__BID/
│   │   │   │   ├── BID ENERGY 04_05_2022__padrao_2__14023604000168__31122021__e26b3998.xlsx
│   │   │   │   ├── BID_12.06.2024__padrao_3__14023604000168__31122023__b0bda683.xlsx
│   │   │   │   └── BID_13102023__padrao_3__14023604000168__31122022__1cd5db0c.xlsx
│   │   │   ├── 14167541000113__AGE_ENERGIA/
│   │   │   │   └── AGE COMERCIALIZADORA 30062026__padrao_6__14167541000113__31122025__3e8ceac0.xlsx
│   │   │   ├── 14295008000137__CTGBRNE/
│   │   │   │   ├── CTG 24092025__padrao_3__14295008000137__21032025__78460486.xlsx
│   │   │   │   ├── CTG BRNE_28.08.2024__padrao_3__14295008000137__31122023__7a62e419.xlsx
│   │   │   │   ├── CTG NE 02022024__padrao_3__14295008000137__31122022__6aa1614e.xlsx
│   │   │   │   ├── CTGBRNE 10042026__padrao_6__14295008000137__31122024__e84a60a7.xlsx
│   │   │   │   └── CTGNE 23072026__padrao_6__14295008000137__31122025__c99e458d.xlsx
│   │   │   ├── 14555633000170__BEP/
│   │   │   │   ├── BEP 08_06_2022__padrao_2__14555633000170__31122021__da6943c0.xlsx
│   │   │   │   ├── BEP 09072025 - Copia__padrao_3__14555633000170__31122024__35418ac7.xlsx
│   │   │   │   ├── BEP 31_08_2021__padrao_2__14555633000170__31122020__71a5b8fb.xlsx
│   │   │   │   ├── BEP ENERGIA RATING 24032026__padrao_6__14555633000170__31122025__d51902d4.xlsx
│   │   │   │   └── BEP_16.05.2024__padrao_6__14555633000170__31122023__ecaafd9f.xlsx
│   │   │   ├── 14609649000119__BOVEN_ENERGIA/
│   │   │   │   ├── BOVEN 27_06_2022__padrao_2__14609649000119__31122021__3c276730.xlsx
│   │   │   │   ├── BOVEN 28032024__padrao_3__14609649000119__31122023__ad708f73.xlsx
│   │   │   │   └── FICHA BOVEN_16.06.2023__padrao_3__14609649000119__31122022__9f48f084.xlsx
│   │   │   ├── 15027346000150__MEGA_WATT/
│   │   │   │   └── MEGA WATT_26_10_2021__padrao_2__15027346000150__31122020__63de4112.xlsx
│   │   │   ├── 15042149000100__LOG_ENERGIA/
│   │   │   │   ├── LOG 27112023__padrao_6__15042149000100__31122022__4ef3cc29.xlsx
│   │   │   │   ├── LOG ENERGIA 01_06_2022__padrao_2__15042149000100__31122021__c29458e8.xlsx
│   │   │   │   ├── LOG ENERGIA 29092025__padrao_3__15042149000100__31122024__f1f2d555.xlsx
│   │   │   │   ├── LOG_10_09_2021__padrao_2__15042149000100__31122020__a6427357.xlsx
│   │   │   │   └── LOG_17.05.2024__padrao_3__15042149000100__31122023__eb3bf814.xlsx
│   │   │   ├── 15054480000140__MEGA/
│   │   │   │   ├── MEGA 04_07_2022__padrao_2__15054480000140__31122021__007a1672.xlsx
│   │   │   │   ├── MEGA_12052023__padrao_4__15054480000140__31122022__5105964e.xlsx
│   │   │   │   ├── MEGA_16_09_2021__padrao_2__15054480000140__31122020__c5563bf8.xlsx
│   │   │   │   └── MEGA_20.06.2024__padrao_3__15054480000140__31122023__020c4e30.xlsx
│   │   │   ├── 15087610000141__ELETRON/
│   │   │   │   ├── ECEL - ELETRON_03_09_2021__padrao_2__15087610000141__31122020__db966111.xlsx
│   │   │   │   └── ELETRON 30_05_2022__padrao_2__15087610000141__31122021__90074bfa.xlsx
│   │   │   ├── 15458171000136__MIGRATIO/
│   │   │   │   ├── MIGRATIO 02072025__padrao_3__15458171000136__31122024__b8ed4f47.xlsx
│   │   │   │   ├── MIGRATIO 02_06_2022__padrao_2__15458171000136__31122021__00244288.xlsx
│   │   │   │   ├── Migratio_07062023__padrao_3__15458171000136__31122022__225ebb2c.xlsx
│   │   │   │   └── MIGRATIO_17_06_2021__padrao_2__15458171000136__31122020__7be0d074.xlsx
│   │   │   ├── 15623286000139__AGORA_ENERGIA/
│   │   │   │   ├── AGORA ENERGIA 09062026__padrao_6__15623286000139__31122025__e095038d.xlsx
│   │   │   │   └── AGORA21.05.2024__padrao_6__15623286000139__31122023__6168402a.xlsx
│   │   │   ├── 15667402000111__SIMPLE_ENERGY/
│   │   │   │   └── SIMPLE 02072026__padrao_6__15667402000111__31122025__f476c794.xlsx
│   │   │   ├── 15728576000147__ATIAIA/
│   │   │   │   ├── ATIAIA 18082026__padrao_6__15728576000147__31122025__7465779d.xlsx
│   │   │   │   ├── ATIAIA 24062025__padrao_3__15728576000147__31122024__5239f515.xlsx
│   │   │   │   └── ATIAIA RATING 06022026__padrao_6__15728576000147__31122024__17baa2fa.xlsx
│   │   │   ├── 15732189000184__IFT_ENERGIA/
│   │   │   │   ├── IFT 04-05-2026__padrao_6__15732189000184__31122024__baa1490f.xlsx
│   │   │   │   ├── IFT COM 27112023__padrao_3__15732189000184__31122022__a30fd095.xlsx
│   │   │   │   ├── IFT_09_09_2021__padrao_2__15732189000184__31122020__d30c00f3.xlsx
│   │   │   │   └── INFINITY 08_08_2022__padrao_2__15732189000184__31122021__4fd5c0d8.xlsx
│   │   │   ├── 16404287000155__SUZANO_CEL_N/
│   │   │   │   └── SUZANO 13122023__padrao_6__16404287000155__31122022__7b19111e.xlsx
│   │   │   ├── 16404287067730__SUZANO_ES_COM/
│   │   │   │   └── SUZANO_04.07.2024__padrao_6__16404287067730__31122023__8e8e10b6.xlsx
│   │   │   ├── 16587133000146__AMAGGI_COMER/
│   │   │   │   ├── AMAGGI 11_07_2022__padrao_2__16587133000146__31122021__24864266.xlsx
│   │   │   │   └── AMAGGI RATING 05022026__padrao_6__16587133000146__31122024__4c058416.xlsx
│   │   │   ├── 16775973000132__RIO_ENERGY/
│   │   │   │   ├── RIO ENERGY 17_11_2021__padrao_2__16775973000132__05022021__9c912766.xlsx
│   │   │   │   └── Rio Energy_28032023__padrao_3__16775973000132__31122022__eb110012.xlsx
│   │   │   ├── 16974249000138__GALP/
│   │   │   │   ├── GALP 11122023__padrao_6__16974249000138__31122022__084ec7f7.xlsx
│   │   │   │   ├── GALP 25112024__padrao_6__16974249000138__31122023__f2117de9.xlsx
│   │   │   │   └── GALP 27082025__padrao_3__16974249000138__31122024__c75d513f.xlsx
│   │   │   ├── 17040615000144__PRIME_ENERGY_CON/
│   │   │   │   └── PRIME ENERGY 02_06_2022__padrao_2__17040615000144__31122021__f08a2704.xlsx
│   │   │   ├── 17070597000143__IDEAL_ENERGIA/
│   │   │   │   ├── IDEAL 25_05_2022 TESTE__padrao_2__17070597000143__31122021__2bc7c825.xlsx
│   │   │   │   └── IDEAL_09_09_2021__padrao_2__17070597000143__31122020__d80944d4.xlsx
│   │   │   ├── 17077752000153__TRINITY_ENERGIA/
│   │   │   │   ├── TRINITY 06_06_2022__padrao_2__17077752000153__31122021__ba876f81.xlsx
│   │   │   │   ├── TRINITY ENERGIA_09_06_2021__padrao_2__17077752000153__31122020__ef69f26d.xlsx
│   │   │   │   └── TRINITY_16.05.2024 v2__padrao_6__17077752000153__31122023__94ce3039.xlsx
│   │   │   ├── 17112981000161__SIMPLE/
│   │   │   │   ├── SIMPLE 06_06_2022__padrao_2__17112981000161__31122021__b655fe19.xlsx
│   │   │   │   ├── SIMPLE 27032024__padrao_6__17112981000161__31122023__b5de56ff.xlsx
│   │   │   │   ├── SIMPLE _14_06_2021__padrao_2__17112981000161__31122020__8850d969.xlsx
│   │   │   │   └── SIMPLE_2024__padrao_3__17112981000161__31122024__a77a62ff.xlsx
│   │   │   ├── 17155730000164__CEMIG_H_COMERCIALIZACAO/
│   │   │   │   ├── CEMIG_09062023__padrao_3__17155730000164__31122022__a2e0b5ed.xlsx
│   │   │   │   ├── CEMIG_13.06.2024__padrao_3__17155730000164__31122023__37922637.xlsx
│   │   │   │   └── CEMIG_24092025__padrao_3__17155730000164__03092025__76ed85dc.xlsx
│   │   │   ├── 17204923000168__RENOVA_COM/
│   │   │   │   ├── RENOVA 12062026__padrao_6__17204923000168__31122025__3e542cef.xlsx
│   │   │   │   ├── RENOVA 26082025__padrao_3__17204923000168__31122024__86b07de8.xlsx
│   │   │   │   ├── RENOVA BR RI__padrao_6__17204923000168__31122024__0e08d072.xlsx
│   │   │   │   └── RENOVA COM 27082025__padrao_3__17204923000168__31122024__281cb87f.xlsx
│   │   │   ├── 17302990000115__CANADIAN_SOLAR/
│   │   │   │   └── CANADIAN RATING 21012026__padrao_6__17302990000115__31122024__6b90af6a.xlsx
│   │   │   ├── 17386017000121__ZETA_ENERGIA/
│   │   │   │   ├── FICHA MODELO_xx.xx.2024__padrao_6__17386017000121__31122023__ad29fd5d.xlsx
│   │   │   │   ├── ZETA 18_04_2022__padrao_2__17386017000121__31122021__b4b1f5ab.xlsx
│   │   │   │   └── ZETA Energia_16_06_2021__padrao_2__17386017000121__31122020__f7525be6.xlsx
│   │   │   ├── 17469701000177__ARCELOR_JF_COM/
│   │   │   │   └── ARCELORMITTAL_21.05.2024__padrao_3__17469701000177__31122023__8a8eb40c.xlsx
│   │   │   ├── 17858631000149__MATRIX_COM/
│   │   │   │   ├── Matrix -grupo- 03042025(Recuperado Autom__padrao_3__17858631000149__31122024__fcbd7d96.xlsx
│   │   │   │   ├── MATRIX 26_05_2022__padrao_2__17858631000149__31122021__6f9541c0.xlsx
│   │   │   │   ├── MATRIX COM 17072026__padrao_6__17858631000149__31122025__ae8a1177.xlsx
│   │   │   │   ├── Matrix Grupo 1 11032024__padrao_3__17858631000149__31122022__abffc18f.xlsx
│   │   │   │   ├── MATRIX_18_06_2021__padrao_2__17858631000149__31122020__3c2f6c35.xlsx
│   │   │   │   ├── MATRIX_19.06.2024__padrao_6__17858631000149__31122023__ab4ec03c.xlsx
│   │   │   │   └── MATRIX_PURA_03042025__padrao_3__17858631000149__31122024__702ddb11.xlsx
│   │   │   ├── 18185035000108__TRUE/
│   │   │   │   ├── TRUE 14042026__padrao_6__18185035000108__31122025__6f808d56.xlsx
│   │   │   │   ├── TRUE 22-05-2025__padrao_3__18185035000108__31122024__52cd156f.xlsx
│   │   │   │   ├── TRUE 22_03_2022__padrao_2__18185035000108__31122021__dce12cfc.xlsx
│   │   │   │   ├── TRUE 29 04 2024__padrao_6__18185035000108__31122023__ab87271f.xlsx
│   │   │   │   └── TRUE _06_05_2021__padrao_2__18185035000108__31122020__25dbfd0d.xlsx
│   │   │   ├── 18384740000134__GRUPO_BC/
│   │   │   │   ├── BC 06_05_2022__padrao_2__18384740000134__31122021__58170c6c.xlsx
│   │   │   │   ├── BC COMERCIALIZADORA 27032026__padrao_6__18384740000134__31122024__10587ef8.xlsx
│   │   │   │   └── BC_05042024__padrao_3__18384740000134__31122023__693fee93.xlsx
│   │   │   ├── 18416364000112__ENERCORE_C/
│   │   │   │   ├── ENERCORE 01072026__padrao_6__18416364000112__31122025__6e4eb1d8.xlsx
│   │   │   │   ├── ENERCORE 07_04_2022__padrao_2__18416364000112__31122021__0499e125.xlsx
│   │   │   │   ├── ENERCORE_11042024__padrao_3__18416364000112__31122023__a29d0755.xlsx
│   │   │   │   ├── ENERCORE_2024__padrao_3__18416364000112__31122024__2bbf75e0.xlsx
│   │   │   │   └── ENERCORE_22032023__padrao_3__18416364000112__31122022__e26580ab.xlsx
│   │   │   ├── 18483400000160__GENIAL_ENERGY/
│   │   │   │   ├── GENIAL 12_04_2022__padrao_2__18483400000160__31122021__27639d35.xlsx
│   │   │   │   ├── Genial 20052025__padrao_3__18483400000160__31122024__f40c5b91.xlsx
│   │   │   │   ├── GENIAL 27102023__padrao_3__18483400000160__31122022__e2b1ffbc.xlsx
│   │   │   │   ├── GENIAL ENERGY 15072026__padrao_6__18483400000160__31122025__b01b333b.xlsx
│   │   │   │   ├── GENIAL_06_09_2021__padrao_2__18483400000160__31122020__d7aecd1e.xlsx
│   │   │   │   └── GENIAL_17.05.2024__padrao_3__18483400000160__31122023__110d0711.xlsx
│   │   │   ├── 19125927000186__COPEL_COM/
│   │   │   │   ├── COPEL_23.07.2024__padrao_3__19125927000186__31122023__7a3ea1a7.xlsx
│   │   │   │   └── COPELCOM_16_04_2021__padrao_2__19125927000186__31122020__a394155f.xlsx
│   │   │   ├── 19502690000105__CE_ANGELIM/
│   │   │   │   └── ANGELIM 09062026__padrao_6__19502690000105__31122025__d06c5420.xlsx
│   │   │   ├── 20557422000170__LIBRA_ENERGIA/
│   │   │   │   ├── LIBRA 05052026__padrao_6__20557422000170__31122025__68d283fa.xlsx
│   │   │   │   ├── LIBRA 29 04 2024__padrao_6__20557422000170__31122023__d85df5da.xlsx
│   │   │   │   ├── LIBRA 30_05_2022__padrao_2__20557422000170__31122021__d4173325.xlsx
│   │   │   │   ├── LIBRA COMERCIALIZADORA 01102025__padrao_3__20557422000170__31122024__1cde6f8d.xlsx
│   │   │   │   ├── LIBRA COMERCIALIZADORA 27032026__padrao_6__20557422000170__31122024__e650d426.xlsx
│   │   │   │   ├── LIBRA_09_09_2021__padrao_2__20557422000170__31122020__0be72f07.xlsx
│   │   │   │   └── LIBRA_2024__padrao_3__20557422000170__31122024__ce144345.xlsx
│   │   │   ├── 20591154000102__ADN_ENERGIA/
│   │   │   │   └── ADN 02062026__padrao_6__20591154000102__31122025__b8df8c05.xlsx
│   │   │   ├── 20726794000182__TESLACOM/
│   │   │   │   └── TESLA 06_06_2022__padrao_2__20726794000182__31122021__1a5b1de1.xlsx
│   │   │   ├── 20978264000121__ENERGETICA_COMERCIALIZADORA/
│   │   │   │   └── ENERGETICA 03_03_2022__padrao_2__20978264000121__31122021__3f7a2d5e.xlsx
│   │   │   ├── 21256386000177__EVEREST_ENERGIA/
│   │   │   │   ├── EVEREST 06_05_2022__padrao_2__21256386000177__31122021__c03f7892.xlsx
│   │   │   │   └── EVEREST_03_09_2021__padrao_2__21256386000177__31122020__63dabfbe.xlsx
│   │   │   ├── 21366458000139__IFSIDA/
│   │   │   │   └── ISFIDA RATING 05032026__padrao_6__21366458000139__31122024__7231d37a.xlsx
│   │   │   ├── 21467516000110__PCH_MOINHO_2/
│   │   │   │   └── PCH MOINHO  RATING 26012026__padrao_6__21467516000110__31122024__8df084e0.xlsx
│   │   │   ├── 21484454000155__MERCATTO_COM/
│   │   │   │   └── MERCATTO COM RATING 14012026__padrao_6__21484454000155__31122024__126451a6.xlsx
│   │   │   ├── 21484454000155__MERCATTO_ENERGIA/
│   │   │   │   └── MERCATTOENERGIA_13.05.2024__padrao_3__21484454000155__31122023__59737d54.xlsx
│   │   │   ├── 21642355000154__ARGON/
│   │   │   │   └── FICHA ARGON_16.06.2023__padrao_3__21642355000154__31122022__42c92bc5.xlsx
│   │   │   ├── 21812954000179__EDF_EN_DO_BRASIL_PARTICIPACOES_LTDA/
│   │   │   │   └── EDF 01042026__padrao_6__21812954000179__31122024__941a581f.xlsx
│   │   │   ├── 22109465000118__HYDRO_ENERGIA/
│   │   │   │   ├── HYDRO Energia 27022024__padrao_6__22109465000118__31122022__8125538b.xlsx
│   │   │   │   ├── HYDRO ENERGIA_2024__padrao_3__22109465000118__31122024__162611bb.xlsx
│   │   │   │   ├── HYDROENERGIA_19.06.2024__padrao_6__22109465000118__31122023__cfdbbc5f.xlsx
│   │   │   │   ├── NORSK HYDRO 16042026__padrao_6__22109465000118__31122025__7323a0ca.xlsx
│   │   │   │   └── NORSK HYDRO ENERGIA 09072026__padrao_6__22109465000118__31122025__a3b44950.xlsx
│   │   │   ├── 22153641000119__POWER_TRADE/
│   │   │   │   └── POWER COM 02_05_2022__padrao_2__22153641000119__31122021__f61cf2f4.xlsx
│   │   │   ├── 22587687000146__UTE_MONTE_ALEGRE_APE/
│   │   │   │   └── USINA MONTE ALEGRE 15072026__padrao_6__22587687000146__31122025__2d3f4b22.xlsx
│   │   │   ├── 22976970000160__PCH_NOVA_GUAPORE/
│   │   │   │   ├── NOVA GUAPORE 12082026__padrao_6__22976970000160__31122025__ee710d7b.xlsx
│   │   │   │   └── PCH - NOVA GUARPORE RATING__padrao_6__22976970000160__31122024__944c1420.xlsx
│   │   │   ├── 23096269000119__REPESA/
│   │   │   │   └── Rio Parana 14042026__padrao_6__23096269000119__31122024__2df8c55e.xlsx
│   │   │   ├── 23412242000198__BEM_COMERCIALIZADORA/
│   │   │   │   └── BEM 10062026__padrao_6__23412242000198__31122025__7a0ff343.xlsx
│   │   │   ├── 23412242000198__PACTO_COMERCIALIZADORA/
│   │   │   │   ├── PACTO 25 04 2024__padrao_6__23412242000198__31122023__7cbf7dd5.xlsx
│   │   │   │   ├── PACTO_11.08.2023__padrao_3__23412242000198__31122022__f4df26df.xlsx
│   │   │   │   └── PACTO_2024__padrao_3__23412242000198__31122024__5218a1c5.xlsx
│   │   │   ├── 23422037000103__SGS/
│   │   │   │   └── SGS BRASIL 10_03_2022__padrao_2__23422037000103__31122021__ed2b87d7.xlsx
│   │   │   ├── 24011952000179__SERRA_DAS_VACAS/
│   │   │   │   └── SERRA DAS VACAS HOLDING II__padrao_6__24011952000179__31122025__f7d815cc.xlsx
│   │   │   ├── 24222394000190__BIOENERGETICA_BOA_VISTA/
│   │   │   │   └── BIOENERGETICA BOA VISTA RATING 03022026__padrao_6__24222394000190__31032025__f1dc9afe.xlsx
│   │   │   ├── 24337192000194__ATLAS_COM/
│   │   │   │   └── ATLAS_18022025__padrao_3__24337192000194__31122023__7d8dc8e0.xlsx
│   │   │   ├── 24479976000157__INFINITYENERGIAS/
│   │   │   │   ├── INFINITY 04-05-2026__padrao_6__24479976000157__31122024__ac19ff57.xlsx
│   │   │   │   ├── INFINITY ENERGIAS 29_11_2021__padrao_2__24479976000157__31122020__2294e392.xlsx
│   │   │   │   ├── Infinity_17.08.2023__padrao_3__24479976000157__31122022__8e52a1ea.xlsx
│   │   │   │   └── INFINITY_20.05.2024 v2__padrao_3__24479976000157__31122023__09c71383.xlsx
│   │   │   ├── 24510849000173__MINERVA_COM/
│   │   │   │   ├── MINERVA 02_06_2022__padrao_2__24510849000173__31122021__ec4aeff3.xlsx
│   │   │   │   ├── MINERVA 05_06_2025__padrao_3__24510849000173__31122024__b84e37de.xlsx
│   │   │   │   ├── MINERVA 25 04 2024__padrao_6__24510849000173__31122023__af341e14.xlsx
│   │   │   │   ├── MINERVA COM 04082026__padrao_6__24510849000173__31122025__8a825089.xlsx
│   │   │   │   ├── MINERVA RATING__padrao_6__24510849000173__31122024__3ae79617.xlsx
│   │   │   │   └── Minerva_12062023__padrao_3__24510849000173__31122022__86e230cf.xlsx
│   │   │   ├── 24550050000100__JARDIM_BOTANICO/
│   │   │   │   └── JARDIM BOTÂNICO GERAÇÃO 06052026__padrao_6__24550050000100__31122025__e2c3651c.xlsx
│   │   │   ├── 24743678000122__ECHOENERGIA_PARTICIPACÕES/
│   │   │   │   └── ECHOENERGIA_09_09_2021__padrao_2__24743678000122__31122020__bcb4c850.xlsx
│   │   │   ├── 25099255000184__STIMA_ENERGIA/
│   │   │   │   ├── STIMA 06_06_2022__padrao_2__25099255000184__31122021__9b2e48bb.xlsx
│   │   │   │   ├── STIMA 11042024__padrao_6__25099255000184__31122023__645a1ce6.xlsx
│   │   │   │   ├── STIMA_10_09_2021__padrao_2__25099255000184__31122020__1cd9a896.xlsx
│   │   │   │   ├── Stima_2024__padrao_3__25099255000184__31122024__3e98ba82.xlsx
│   │   │   │   └── STIMA_30052023__padrao_4__25099255000184__31122022__6526e919.xlsx
│   │   │   ├── 25318541000193__APOLLO_C/
│   │   │   │   └── APOLLO 08 05 2024__padrao_3__25318541000193__31122023__9bf42e45.xlsx
│   │   │   ├── 25319200000132__HUMAITA_COM/
│   │   │   │   └── HUMAITA 09062025__padrao_3__25319200000132__31122024__8478ec71.xlsx
│   │   │   ├── 25369840000157__COMERC_PART/
│   │   │   │   ├── COMERC 29 04 2024__padrao_3__25369840000157__31122023__38814998.xlsx
│   │   │   │   ├── COMERC PART 23072026__padrao_6__25369840000157__31122025__9742e0b4.xlsx
│   │   │   │   ├── COMERC Participações 28112023__padrao_3__25369840000157__31122022__15650f7c.xlsx
│   │   │   │   └── VIBRA ENERGIA RATING 06112025__padrao_7__25369840000157__31122024__5e6d60f2.xlsx
│   │   │   ├── 25466251000197__ENECEL/
│   │   │   │   ├── ENECEL_03_09_2021__padrao_2__25466251000197__31122020__d4374007.xlsx
│   │   │   │   └── ENECEL_26.06.2024__padrao_3__25466251000197__31122023__09a6c61b.xlsx
│   │   │   ├── 26215280000149__CSI_C/
│   │   │   │   └── CANADIAN 08062026__padrao_6__26215280000149__31122025__2aac8fb2.xlsx
│   │   │   ├── 26474919000100__MERITO_ENERGIA/
│   │   │   │   ├── MERITO 14_11_2022__padrao_2__26474919000100__31122021__217e5f6d.xlsx
│   │   │   │   └── MERITO_18_06_2021__padrao_2__26474919000100__31122020__c51b9340.xlsx
│   │   │   ├── 26537119000191__VIVAZ_ENERGIA/
│   │   │   │   └── VIVAZ ENERGIA 15_06_2022__padrao_2__26537119000191__31122021__f3bbdbe1.xlsx
│   │   │   ├── 26562346000177__RZK/
│   │   │   │   ├── RZK 10112023__padrao_6__26562346000177__31122022__4b24aa1a.xlsx
│   │   │   │   ├── RZK_16.05.2024__padrao_3__26562346000177__31122023__bee67ee6.xlsx
│   │   │   │   ├── RZK_26_10_2021__padrao_2__26562346000177__31122020__5257321f.xlsx
│   │   │   │   ├── THOPEN 09072025__padrao_3__26562346000177__31122024__1f16466d.xlsx
│   │   │   │   └── THOPEN ENERGY RATING 28112025__padrao_6__26562346000177__31122024__19295889.xlsx
│   │   │   ├── 26914969000161__EXPONENCIAL_ENERGIA/
│   │   │   │   ├── EXPONENCIAL 01112024__padrao_3__26914969000161__31122023__73abf9fe.xlsx
│   │   │   │   ├── EXPONENCIAL 10_03_2022__padrao_2__26914969000161__31122021__17293803.xlsx
│   │   │   │   └── FICHA EXPONENCIAL_16.06.2023__padrao_3__26914969000161__31122022__2fc69327.xlsx
│   │   │   ├── 26914969000161__ULTRAGAZ_COM/
│   │   │   │   ├── ULTRAGAZ 12122025__padrao_6__26914969000161__31122024__b49341d0.xlsx
│   │   │   │   └── ULTRAGAZ 14052026__padrao_6__26914969000161__31122025__eb5d020c.xlsx
│   │   │   ├── 26940979000171__ESFERA_COM/
│   │   │   │   ├── ESFERA 02_08_2022__padrao_2__26940979000171__31122021__b19f3b41.xlsx
│   │   │   │   ├── ESFERA 26 04 2024__padrao_6__26940979000171__31122023__7cc6090c.xlsx
│   │   │   │   └── ESFERA 27022024__padrao_6__26940979000171__31122022__1382b4b3.xlsx
│   │   │   ├── 26986376000100__IPIRA_ENERGIA_S.A/
│   │   │   │   └── IPIRA Energia S.A. - 00484431__padrao_6__26986376000100__31122025__2493b76a.xlsx
│   │   │   ├── 27184790000169__CONVEX/
│   │   │   │   └── CONVEX 18082026__padrao_6__27184790000169__31122025__20d607fd.xlsx
│   │   │   ├── 27352303000120__UHE_SAO_SIMAO/
│   │   │   │   └── UHE SAO SIMAO 14052026__padrao_6__27352303000120__31122025__40e2d1e9.xlsx
│   │   │   ├── 27483435000190__FOTOVO/
│   │   │   │   ├── FOTOVO 01_09_2022__padrao_2__27483435000190__31122021__6a2f6e4e.xlsx
│   │   │   │   ├── FOTOVO 30-04-2026__padrao_6__27483435000190__31122024__a90c23b1.xlsx
│   │   │   │   ├── FOTOVO_11.08.2023___padrao_4__27483435000190__31122022__eb6cbd02.xlsx
│   │   │   │   └── FOTOVO_21.05.2024__padrao_6__27483435000190__31122023__a3de2533.xlsx
│   │   │   ├── 27690671000188__THERA_TRADING/
│   │   │   │   ├── THERA 08_08_2022__padrao_2__27690671000188__31122021__99f5d45d.xlsx
│   │   │   │   ├── THERA 30102025__padrao_6__27690671000188__31122024__98c33add.xlsx
│   │   │   │   ├── THERA_04.06.2024__padrao_6__27690671000188__31122023__f4ba3508.xlsx
│   │   │   │   ├── THERA_08_06_2021__padrao_2__27690671000188__31122020__7d8f1ec0.xlsx
│   │   │   │   └── THERA_10102023__padrao_3__27690671000188__31122022__59136fd4.xlsx
│   │   │   ├── 27796415000170__SEB_-_SHELL_ENERGY_BRASIL/
│   │   │   │   ├── SEB 16102024__1__padrao_3__27796415000170__31122023__639eb619.xlsx
│   │   │   │   ├── SEB RATING 17112025__padrao_6__27796415000170__31122024__a3afa918.xlsx
│   │   │   │   ├── SEB RATING 2023__padrao_6__27796415000170__31122024__45a59683.xlsx
│   │   │   │   ├── SHELL 07052026__padrao_6__27796415000170__31122025__0fbd1222.xlsx
│   │   │   │   └── SHELL ENERGY 08_08_2022__padrao_2__27796415000170__31122021__cafc6c51.xlsx
│   │   │   ├── 27796415000250__SEB_-_SHELL_ENERGY_BRASIL/
│   │   │   │   └── SEB 16102024__padrao_3__27796415000250__31122023__51772d3f.xlsx
│   │   │   ├── 28120534000170__PETRACOM/
│   │   │   │   ├── PETRA 09_03_ 2022__padrao_2__28120534000170__31122021__f297efd3.xlsx
│   │   │   │   └── PETRA_06_05_2021( modelo novo)__padrao_2__28120534000170__31122020__185fe1b2.xlsx
│   │   │   ├── 28133664000148__THOPEN/
│   │   │   │   └── THOPEN ENERGIA 20072026__padrao_6__28133664000148__31122024__23cda899.xlsx
│   │   │   ├── 28397998000129__LUX/
│   │   │   │   ├── FICHA MODELO_xx.xx.xxxx__4__padrao_6__28397998000129__31122023__d068688a.xlsx
│   │   │   │   ├── FICHA MODELO_xx.xx.xxxx__padrao_6__28397998000129__31122022__29bf6542.xlsx
│   │   │   │   ├── LUX 01_06_2022__padrao_2__28397998000129__31122021__8d1ee995.xlsx
│   │   │   │   ├── LUX 19082026__padrao_6__28397998000129__31122025__edec85fc.xlsx
│   │   │   │   ├── LUX 21052025__padrao_3__28397998000129__31122024__3bba6dae.xlsx
│   │   │   │   └── LUX RATING 02032026__padrao_6__28397998000129__31122024__09e3ba09.xlsx
│   │   │   ├── 28423185000166__WORLD_SE_COM/
│   │   │   │   └── WORLDSE_20.06.2024__padrao_6__28423185000166__31122023__b968a36b.xlsx
│   │   │   ├── 28640358000106__EKOA_ENERGIA/
│   │   │   │   ├── EKOA 06_06_2022__padrao_2__28640358000106__31122021__4b56f384.xlsx
│   │   │   │   └── EKOA_03_09_2021__padrao_2__28640358000106__31122020__63566cb7.xlsx
│   │   │   ├── 28758086000135__NEWCOM/
│   │   │   │   ├── NEW COM 02_08_2022__padrao_2__28758086000135__31122021__d52c740b.xlsx
│   │   │   │   ├── NEWCOM RATING 27012026__padrao_6__28758086000135__31122024__66c7f27b.xlsx
│   │   │   │   ├── NEWCOM_09102024__padrao_3__28758086000135__31122023__943529c1.xlsx
│   │   │   │   └── NEWCOM_19072023__padrao_3__28758086000135__31122022__22fec522.xlsx
│   │   │   ├── 28803705000166__GO_ENERGY/
│   │   │   │   ├── GO ENERGY 25_05_2022__padrao_2__28803705000166__31122021__1a677df1.xlsx
│   │   │   │   └── GO ENERGY 29_11_2021__padrao_2__28803705000166__31122020__adecf520.xlsx
│   │   │   ├── 29000095000125__TEMPO_ENERGIA/
│   │   │   │   ├── TEMPO 08_08_2022__padrao_2__29000095000125__31122021__64d11f0d.xlsx
│   │   │   │   ├── TEMPO 20112023__padrao_6__29000095000125__31122022__d18b5780.xlsx
│   │   │   │   ├── Tempo Energia_10_06_2021__padrao_2__29000095000125__31122020__4e243f83.xlsx
│   │   │   │   └── TEMPO_21.05.2024__padrao_6__29000095000125__31122023__283b16fa.xlsx
│   │   │   ├── 29198324000168__ABC_BRASIL/
│   │   │   │   ├── ABC 14072026__padrao_6__29198324000168__31122025__c231ff50.xlsx
│   │   │   │   ├── ABC 29.07.2024__padrao_3__29198324000168__31122023__5361ed62.xlsx
│   │   │   │   ├── ABC BRASIL 15102025__padrao_3__29198324000168__31122024__d50b1666.xlsx
│   │   │   │   └── Banco ABC 05092023__padrao_3__29198324000168__31122022__966513b8.xlsx
│   │   │   ├── 29270235000185__LUDFOR_COMERCIALIZADORA/
│   │   │   │   ├── LUDFOR 08052025__padrao_3__29270235000185__31122024__4af5f07e.xlsx
│   │   │   │   ├── LUDFOR COM 08052025__padrao_3__29270235000185__31122024__27d3b134.xlsx
│   │   │   │   ├── LUDFOR_19062023__padrao_3__29270235000185__31122022__a190fd00.xlsx
│   │   │   │   └── LUDFOR_20.05.2024__padrao_6__29270235000185__31122023__490a8af6.xlsx
│   │   │   ├── 29270235000185__PLURAL_COMERCIALIZADORA/
│   │   │   │   └── PLURAL ENERGIA 20_07_2022__padrao_2__29270235000185__31122021__714c5565.xlsx
│   │   │   ├── 29316596000115__INPASA/
│   │   │   │   └── INPASA 05082026__padrao_6__29316596000115__31122025__bf0bdbdd.xlsx
│   │   │   ├── 29340729000199__SKOPOS_ENERGIA/
│   │   │   │   ├── SKOPOS 02062026__padrao_6__29340729000199__31122025__65cf9a0a.xlsx
│   │   │   │   ├── SKOPOS 08_08_2022__padrao_2__29340729000199__31122021__7a4dc0e5.xlsx
│   │   │   │   ├── SKOPOS 24 04 2024__padrao_6__29340729000199__31122023__478b7aef.xlsx
│   │   │   │   ├── SKOPOS 26082025__padrao_3__29340729000199__31122024__f87033b0.xlsx
│   │   │   │   ├── SKOPOS 27032026 df 2024__padrao_6__29340729000199__31122024__15d135d5.xlsx
│   │   │   │   ├── SKOPOS_09_09_2021__padrao_2__29340729000199__31122020__53fc0659.xlsx
│   │   │   │   └── SKOPOS_14072023__padrao_3__29340729000199__31122022__fc8d1d04.xlsx
│   │   │   ├── 29350168000109__VOLTALIA_COM/
│   │   │   │   ├── SOL SERRA DO MEL VI SPE S.A_20.05.2024__padrao_3__29350168000109__31122023__1732660c.xlsx
│   │   │   │   ├── VOLTALIA RATING 06112025__padrao_7__29350168000109__31122024__137b7dcf.xlsx
│   │   │   │   └── VOLTALIA_2024__padrao_3__29350168000109__31122024__1361c8fd.xlsx
│   │   │   ├── 29362082000104__MERCURIO_TRADING/
│   │   │   │   └── MERCURIO_13.05.2024__padrao_6__29362082000104__31122023__1778b966.xlsx
│   │   │   ├── 29362082000104__TYR_TRADING/
│   │   │   │   └── TYR 16072025__padrao_3__29362082000104__31122024__c52a0fab.xlsx
│   │   │   ├── 29883520000171__PWR_ENERGIA/
│   │   │   │   ├── POWER COM 14_06_2022__padrao_2__29883520000171__31122021__3273497e.xlsx
│   │   │   │   └── PWR ENERGIA_15_06_2021__padrao_2__29883520000171__31122020__b32a6c89.xlsx
│   │   │   ├── 29915125000123__ALBIOMA/
│   │   │   │   └── ALBIOMA 09072026__padrao_6__29915125000123__31122025__fb0d87b8.xlsx
│   │   │   ├── 29993083000149__BARIGUI_ENERGIA/
│   │   │   │   ├── BARIGUI_17.05.2024__padrao_3__29993083000149__31122023__0eb64eae.xlsx
│   │   │   │   └── BARIGUI_17032023__padrao_4__29993083000149__31122022__a0b5182c.xlsx
│   │   │   ├── 29993083000149__EEI/
│   │   │   │   └── EEI BARIGUI_04_02_2022 divididos por 12__padrao_2__29993083000149__31122021__ae974cff.xlsx
│   │   │   ├── 30124679000191__DESTTRA_ENERGIA/
│   │   │   │   └── DESTTRA_02_09_2021__padrao_2__30124679000191__31122020__f852d5fa.xlsx
│   │   │   ├── 30195195000133__BOREAL_COM/
│   │   │   │   ├── BOREAL 17_05_2022__padrao_2__30195195000133__31122021__bc32ab7b.xlsx
│   │   │   │   └── BOREAL_01_09_2021__padrao_2__30195195000133__31122020__e65de90c.xlsx
│   │   │   ├── 30206620000142__VIX_ENERGIA/
│   │   │   │   └── VIX 17_11_2021__padrao_2__30206620000142__31122020__433405d4.xlsx
│   │   │   ├── 30248458000125__ENEL_TRADING/
│   │   │   │   ├── ENEL TRADING 27112023__padrao_3__30248458000125__31122022__8b8f99c4.xlsx
│   │   │   │   └── ENEL_29.07.2024__padrao_3__30248458000125__31122023__d0ee4997.xlsx
│   │   │   ├── 30248458000125__ENEL_TRADING_BRASIL/
│   │   │   │   └── Enel Brasil_25092025__padrao_3__30248458000125__27082024__bff44514.xlsx
│   │   │   ├── 30306294000145__BANCO_BTG_PACTUAL/
│   │   │   │   └── BTG_05092023__padrao_3__30306294000145__31122022__fa59a299.xlsx
│   │   │   ├── 30306294000226__BTG_PACTUAL_ENERGIA/
│   │   │   │   └── BTG 01102024__padrao_3__30306294000226__31122023__bd2b7877.xlsx
│   │   │   ├── 30483222000173__GOLD_ENERGIA/
│   │   │   │   ├── FICHA GOLD_19.06.2023__padrao_3__30483222000173__31122022__bbe25404.xlsx
│   │   │   │   ├── GOLD 07_04_2022__padrao_2__30483222000173__31122021__cc2293ee.xlsx
│   │   │   │   ├── GOLD 27032024 - Copia__padrao_6__30483222000173__31122023__505ee973.xlsx
│   │   │   │   └── GOLD _05_05_2021__padrao_2__30483222000173__31122020__4a4591e6.xlsx
│   │   │   ├── 30693787000185__ENERGIZOU/
│   │   │   │   └── ENERGIZOU_05.06.2024__padrao_6__30693787000185__31122023__12c7f73e.xlsx
│   │   │   ├── 30693787000185__LIBERTY_ENERGY/
│   │   │   │   └── ENERGIZOU 17_03_2022__padrao_2__30693787000185__31122021__5271a610.xlsx
│   │   │   ├── 30834939000112__FLASH_ENERGY/
│   │   │   │   ├── FLASH 11072025__padrao_3__30834939000112__31122024__83422c0d.xlsx
│   │   │   │   └── FLASH ENERGY 25042024__padrao_6__30834939000112__31122023__86deb931.xlsx
│   │   │   ├── 30840548000100__FLOW/
│   │   │   │   ├── FLOW_03_09_2021__padrao_2__30840548000100__31122021__802ee549.xlsx
│   │   │   │   └── Genco_22_05_2025__padrao_3__30840548000100__31122024__8e613430.xlsx
│   │   │   ├── 30840548000100__GENCO/
│   │   │   │   └── GENCO 23042024__padrao_6__30840548000100__31122023__1f02d39d.xlsx
│   │   │   ├── 30902608000172__EVO_ENERGIA/
│   │   │   │   ├── EVO 20112023__padrao_6__30902608000172__31122022__e5615262.xlsx
│   │   │   │   ├── EVO ENERGIA 27062025__padrao_3__30902608000172__31122024__acb39ff5.xlsx
│   │   │   │   ├── EVO ENERGIA 30_05_2022__padrao_2__30902608000172__31122021__6d923749.xlsx
│   │   │   │   ├── EVO ENERGIA _25_05_2021__padrao_2__30902608000172__31122020__67ecc47c.xlsx
│   │   │   │   └── EVO_20.05.2024__padrao_6__30902608000172__31122023__856baeb1.xlsx
│   │   │   ├── 30929117000115__BRASIL_SERVICOS/
│   │   │   │   ├── BRASIL SERVICOS_08_06_2021__padrao_2__30929117000115__31122020__30342cfb.xlsx
│   │   │   │   └── BRASIL Serviços_18042023__padrao_3__30929117000115__31122022__442f5d30.xlsx
│   │   │   ├── 30966130000144__LEAP_COMERCIALIZADORA/
│   │   │   │   └── Squadra_2024__padrao_3__30966130000144__31122024__9233086b.xlsx
│   │   │   ├── 30966130000144__SQUADRA/
│   │   │   │   ├── SQUADRA 16_11_2022__padrao_2__30966130000144__31082022__5a811e79.xlsx
│   │   │   │   ├── SQUADRA_18 04 2024__padrao_6__30966130000144__31122023__7b58e28d.xlsx
│   │   │   │   └── SQUADRA_29032023__padrao_3__30966130000144__31122022__edf1b141.xlsx
│   │   │   ├── 30983948000175__CENTRAL/
│   │   │   │   ├── CENTRAL 06_05_2022__padrao_2__30983948000175__31122021__62e72943.xlsx
│   │   │   │   ├── CENTRAL 08 05 2024__padrao_6__30983948000175__31122023__3265f642.xlsx
│   │   │   │   └── Central_22_05_2025__padrao_3__30983948000175__31122024__ffe4a8fd.xlsx
│   │   │   ├── 31102147000116__PARATY/
│   │   │   │   ├── PARATY 02_06_2022__padrao_2__31102147000116__31122021__f35fef5b.xlsx
│   │   │   │   ├── Paraty 28062024__padrao_6__31102147000116__31122023__408a2c07.xlsx
│   │   │   │   ├── PARATY ENERGIA 01102025__padrao_3__31102147000116__31122024__67ae7194.xlsx
│   │   │   │   └── Paraty Energia_30052023__padrao_3__31102147000116__31122022__70b3a0d5.xlsx
│   │   │   ├── 31233530000103__ATHENA_COMERCIALIZADORA/
│   │   │   │   └── ATHENA 29_08_2022__padrao_2__31233530000103__31122021__e076cf16.xlsx
│   │   │   ├── 31512081000132__BRAVO_(PERFIL_AGENTE)/
│   │   │   │   ├── BRAVO 08052026__padrao_6__31512081000132__31122025__a3fcc638.xlsx
│   │   │   │   ├── BRAVO 11042024__padrao_6__31512081000132__31122023__3990468c.xlsx
│   │   │   │   ├── Bravo_2024 (Salvo automaticamente)__padrao_3__31512081000132__31122024__7f3677ca.xlsx
│   │   │   │   └── BRAVO_26052023__padrao_3__31512081000132__31122022__45593681.xlsx
│   │   │   ├── 31512081000132__BRAVO_ENERGIA/
│   │   │   │   └── BRAVO_25_10_2021__padrao_2__31512081000132__31122020__701cdbb9.xlsx
│   │   │   ├── 31557781000143__GET_ENERGY_TRADING/
│   │   │   │   └── GET_06_09_2021__padrao_2__31557781000143__31122020__6989cb95.xlsx
│   │   │   ├── 31627849000113__AMBAR_COMERCIALIZADORA/
│   │   │   │   ├── AMBAR 11122023__padrao_3__31627849000113__31122022__118d9d11.xlsx
│   │   │   │   ├── AMBAR 26_04_2022__padrao_2__31627849000113__31122021__7cf8e401.xlsx
│   │   │   │   ├── AMBAR_29.07.2024__padrao_3__31627849000113__31122023__3a55eb58.xlsx
│   │   │   │   ├── AMBAR_31_08_2021__padrao_2__31627849000113__31122020__53c81f1e.xlsx
│   │   │   │   └── J&F RATING 06112025__padrao_7__31627849000113__31122024__6dd82a39.xlsx
│   │   │   ├── 31635668000139__ENGIE_TRADING/
│   │   │   │   ├── ENGIE_06.06.2024__padrao_3__31635668000139__31122023__a39d1402.xlsx
│   │   │   │   └── EngieTrading_05092023__padrao_3__31635668000139__31122022__ac04612c.xlsx
│   │   │   ├── 31781135000165__ITAU_COM/
│   │   │   │   ├── ITAU 13062023__padrao_3__31781135000165__31122022__7985fd04.xlsx
│   │   │   │   ├── ITAU 30102025__padrao_7__31781135000165__31122024__3ff996c5.xlsx
│   │   │   │   ├── ITAU COM 28052026__padrao_6__31781135000165__31122025__1cc173b0.xlsx
│   │   │   │   └── ITAU_05.07.2024__padrao_3__31781135000165__31122023__b55f7a2d.xlsx
│   │   │   ├── 31864869000108__BP/
│   │   │   │   ├── BP COM_04_10_2021__padrao_2__31864869000108__31032021__33623173.xlsx
│   │   │   │   ├── BP Comercializadora_28_01_2022__padrao_2__31864869000108__31122021__a56f4172.xlsx
│   │   │   │   └── BP ENERGIA_23.07.2024__padrao_3__31864869000108__31122023__68a04eba.xlsx
│   │   │   ├── 31897236000104__EVOLUTION_ENERGIA/
│   │   │   │   └── EVOLUTION_19_03_2021__padrao_2__31897236000104__31122020__c82b864f.xlsx
│   │   │   ├── 31932088000103__ECHOENERGIA/
│   │   │   │   ├── Echoenergia Participações__padrao_2__31932088000103__31122020__a4c31967.xlsx
│   │   │   │   └── EQUATORIAL (ECHO)_25092025__padrao_3__31932088000103__31122024__19c71b7a.xlsx
│   │   │   ├── 31932088000103__ECHOENERGIA_COMERCIALIZADORA/
│   │   │   │   ├── ECHOENERGIA 30062026__padrao_6__31932088000103__31122024__dace17c6.xlsx
│   │   │   │   └── EQUATORIAL RENOVAVEIS 08062026__padrao_6__31932088000103__31122024__f95deffa.xlsx
│   │   │   ├── 32023463000165__SANTA_MARIA_ENERGIA/
│   │   │   │   ├── SANTA MARIA 11082026__padrao_6__32023463000165__31122025__55eb85fe.xlsx
│   │   │   │   ├── SANTA MARIA_16.05.2024__padrao_6__32023463000165__31122023__60afd5c4.xlsx
│   │   │   │   └── SANTA MARIA_2024__padrao_3__32023463000165__31122024__a60344ae.xlsx
│   │   │   ├── 32023463000165__SMC/
│   │   │   │   └── SANTA MARIA_09_09_2021__padrao_2__32023463000165__31122020__63627231.xlsx
│   │   │   ├── 32168500000123__OLYMPE/
│   │   │   │   ├── OLYMPE 1311223__padrao_3__32168500000123__31122022__820d073e.xlsx
│   │   │   │   ├── OLYMPE 24042024__padrao_3__32168500000123__31122023__f7c4389b.xlsx
│   │   │   │   └── OLYMPE 26_10_2022__padrao_2__32168500000123__31122021__3b319473.xlsx
│   │   │   ├── 32185360000100__URCA/
│   │   │   │   ├── FICHA URCA_20.06.2023__padrao_3__32185360000100__31122022__e5ecf41d.xlsx
│   │   │   │   ├── URCA 08_08_2022__padrao_2__32185360000100__31122021__9ee38172.xlsx
│   │   │   │   ├── URCA 11 04 2024__padrao_6__32185360000100__31122023__129dbd66.xlsx
│   │   │   │   └── URCA_09_09_2021__padrao_2__32185360000100__31122020__59c3fa43.xlsx
│   │   │   ├── 32234363000188__CEI/
│   │   │   │   ├── CEI 10092025__padrao_3__32234363000188__31122024__42d1536b.xlsx
│   │   │   │   ├── CEI COMERCIALIZADORA 17082026__padrao_6__32234363000188__31122025__a0f84bb7.xlsx
│   │   │   │   └── CEI ENERGETICA 17082026__padrao_6__32234363000188__31122024__97243686.xlsx
│   │   │   ├── 32235159000181__NEWEN/
│   │   │   │   └── NEWEN_09_09_2021__padrao_2__32235159000181__31072020__ea8986d7.xlsx
│   │   │   ├── 32312466000119__INDRA_ENERGIA/
│   │   │   │   ├── INDRA 15_06_2022__padrao_2__32312466000119__31122021__14b06d68.xlsx
│   │   │   │   ├── INDRA 16072025__padrao_3__32312466000119__31122024__c61b94c1.xlsx
│   │   │   │   ├── INDRA_09_09_2021__padrao_2__32312466000119__31122020__b808eb6f.xlsx
│   │   │   │   └── INDRA_11042024__padrao_3__32312466000119__31122023__257706b1.xlsx
│   │   │   ├── 32618447000115__B2R_ENERGIA/
│   │   │   │   ├── B2R 27_06_2022__padrao_2__32618447000115__31122021__48bc53bf.xlsx
│   │   │   │   ├── B2R ENERGIA_20122021__padrao_2__32618447000115__31122020__deb25d25.xlsx
│   │   │   │   └── B2R_22.05.2024__padrao_6__32618447000115__31122023__e75ca729.xlsx
│   │   │   ├── 32618447000115__GRID_ENERGIA/
│   │   │   │   ├── GRID ENERGIA 04092025__padrao_3__32618447000115__31122024__669094fb.xlsx
│   │   │   │   └── GRID ENERGIA 23062026__padrao_6__32618447000115__31122025__6827712a.xlsx
│   │   │   ├── 32618447000620__B2R_ENERGIA_GO/
│   │   │   │   └── B2R_06.06.2024__padrao_3__32618447000620__31122023__11699b5e.xlsx
│   │   │   ├── 32783106000103__W7/
│   │   │   │   └── W7_25_05_2021__padrao_2__32783106000103__31122020__07017edc.xlsx
│   │   │   ├── 33000167000101__PETROBRAS_PIE/
│   │   │   │   └── PETROBRAS PIE 03062025__padrao_3__33000167000101__31122024__c5a25860.xlsx
│   │   │   ├── 33127947000117__LIBERTHA/
│   │   │   │   └── LIBHERTA 01_06_2022__padrao_2__33127947000117__31122021__60731e81.xlsx
│   │   │   ├── 33524912000111__NEWAVECOM/
│   │   │   │   └── NEWAVE 27032026__padrao_6__33524912000111__31122024__712a1d3c.xlsx
│   │   │   ├── 33611500000119__RATING_DE_CRÉDITO_-_ESCALA_NACIONAL/
│   │   │   │   └── Gerdau 01042026__padrao_6__33611500000119__31122024__4e9032f2.xlsx
│   │   │   ├── 33664228000135__BARRALCOOL/
│   │   │   │   └── BARRALCOOL 13072026__padrao_6__33664228000135__31122025__22d453c5.xlsx
│   │   │   ├── 33931753000170__EXATA_ENERGIA/
│   │   │   │   └── EXATA_03_09_2021__padrao_2__33931753000170__31122020__2dfdc41d.xlsx
│   │   │   ├── 33933760000100__CASA_DOS_VENTOS_COM/
│   │   │   │   ├── CASA DOS VENTOS 03 05 2024__padrao_3__33933760000100__31122023__f6e5bda8.xlsx
│   │   │   │   ├── CASA DOS VENTOS 08_06_2022__padrao_2__33933760000100__31122021__f87323ec.xlsx
│   │   │   │   ├── CASA DOS VENTOS 30072026__padrao_6__33933760000100__31122025__b7880a13.xlsx
│   │   │   │   ├── CASA DOS VENTOS RATING 29102025__padrao_7__33933760000100__31122024__1d82f6e7.xlsx
│   │   │   │   └── CASA_DOS_VENTOS_11082023__padrao_3__33933760000100__31122022__5f6a7839.xlsx
│   │   │   ├── 34475373000130__XP_COMERCIALIZADORA/
│   │   │   │   ├── XP 05092025__padrao_3__34475373000130__31122024__17d483e4.xlsx
│   │   │   │   ├── XP 19052025__padrao_3__34475373000130__31122024__9cfed231.xlsx
│   │   │   │   ├── XP COM 17072026__padrao_6__34475373000130__31122025__cb90f295.xlsx
│   │   │   │   ├── XP COMERCIALIZADORA 14_07_2022__padrao_2__34475373000130__31122021__c0fbf2dc.xlsx
│   │   │   │   ├── XP RATING 13112025__padrao_7__34475373000130__31122024__f6e07856.xlsx
│   │   │   │   ├── XP_03112023__padrao_3__34475373000130__31122022__cc88b058.xlsx
│   │   │   │   └── XP_06_09_2021__padrao_2__34475373000130__30062021__4e555fde.xlsx
│   │   │   ├── 34818458000174__VOLTALIA_COM/
│   │   │   │   └── SOL SERRA DO MEL IV SPE S.A_20.05.2024__padrao_3__34818458000174__31122023__d75906ee.xlsx
│   │   │   ├── 34818597000106__VOLTALIA_COM/
│   │   │   │   └── SOL SERRA DO MEL V SPE S.A_20.05.2024__padrao_3__34818597000106__31122023__661184df.xlsx
│   │   │   ├── 34867956000107__PARATY_COMERCIALIZADORA/
│   │   │   │   └── PARATY_05.07.2024__padrao_3__34867956000107__31122023__93ab2aa0.xlsx
│   │   │   ├── 34980728000149__LDC_COM/
│   │   │   │   └── ALCAST_12.07.2024__padrao_3__34980728000149__31122023__f1bb56e9.xlsx
│   │   │   ├── 35224835000100__LUDFOR_PARTICIPACOES/
│   │   │   │   ├── LUDFOR 11062026__padrao_6__35224835000100__31122025__60f48894.xlsx
│   │   │   │   └── Ludfor geradora 16072026__padrao_6__35224835000100__31122025__dcaf5e26.xlsx
│   │   │   ├── 35458657000181__TAKODA_COMERCIALIZADORA/
│   │   │   │   └── TAKODA_13.06.2024__padrao_3__35458657000181__31122023__74ac0319.xlsx
│   │   │   ├── 35487170000127__ZEST/
│   │   │   │   └── ZEST 27062025__padrao_3__35487170000127__31122024__f333d559.xlsx
│   │   │   ├── 35487170000127__ZEST_ENERGIA/
│   │   │   │   ├── ZEST 15042024__padrao_6__35487170000127__31122023__dbff0ddf.xlsx
│   │   │   │   ├── ZEST _05_05_2021(modelo novo)__padrao_2__35487170000127__31122020__d923a06b.xlsx
│   │   │   │   └── ZEST_26_04_2022__padrao_2__35487170000127__31122021__c65c9b88.xlsx
│   │   │   ├── 35823536000191__COPEL_COM/
│   │   │   │   └── JANDAÍRA III ENERGIAS RENOVÁVEIS S.A._23__padrao_3__35823536000191__31122023__b297b155.xlsx
│   │   │   ├── 35823538000180__COPEL_COM/
│   │   │   │   └── JANDAÍRA I ENERGIAS RENOVÁVEIS S.A._23.0__padrao_3__35823538000180__31122023__34e1d98c.xlsx
│   │   │   ├── 35823577000188__COPEL_COM/
│   │   │   │   └── JANDAÍRA IV ENERGIAS RENOVÁVEIS S.A._23.__padrao_3__35823577000188__31122023__511294e3.xlsx
│   │   │   ├── 35824347000133__COPEL_COM/
│   │   │   │   └── JANDAÍRA II ENERGIAS RENOVÁVEIS S.A._23.__padrao_3__35824347000133__31122023__4c716f55.xlsx
│   │   │   ├── 35881121000174__ANGELINA/
│   │   │   │   └── ANGELINA COLOMBO 29072026__padrao_6__35881121000174__31032026__e76d1e65.xlsx
│   │   │   ├── 35881121000174__COLOMBO/
│   │   │   │   └── ANGELINA COLOMBO__padrao_6__35881121000174__31122025__662041cd.xlsx
│   │   │   ├── 35984409000174__EDF_RE_VERDECOM/
│   │   │   │   ├── EDF 06122023__padrao_3__35984409000174__31122022__75471526.xlsx
│   │   │   │   ├── EDF 30062026__padrao_6__35984409000174__31122024__c600a90d.xlsx
│   │   │   │   └── EDF RENEWABLES VERDECOM 03082026__padrao_6__35984409000174__31122025__069474e9.xlsx
│   │   │   ├── 35984409000174__VERDECOM_COMERCIALIZADORA/
│   │   │   │   └── EDF VERDECOM 22082025__padrao_3__35984409000174__31122024__394d6295.xlsx
│   │   │   ├── 36537518000106__MEZ_ENERGIA/
│   │   │   │   └── MEZ 12122023__padrao_6__36537518000106__31122022__f0dc8c61.xlsx
│   │   │   ├── 37028928000194__MERCATTO_COM/
│   │   │   │   └── MERCATTOCOM_13.05.2024__padrao_6__37028928000194__31122023__95c30d88.xlsx
│   │   │   ├── 37543498000149__VOQEN/
│   │   │   │   └── BRASKEN 19 04 2024__padrao_3__37543498000149__31122023__6bb2a17d.xlsx
│   │   │   ├── 37640312000170__MENDUBIM_GERACAO/
│   │   │   │   └── MENDUBIM GERAÇÃO 19112024__padrao_3__37640312000170__31122023__afef9426.xlsx
│   │   │   ├── 38126813000103__NEC_ENERGIA/
│   │   │   │   └── NEC ENERGIA 18082026__padrao_6__38126813000103__31122025__a7b6a589.xlsx
│   │   │   ├── 38154005000141__ARMOR/
│   │   │   │   ├── ARMOR 15082025__padrao_3__38154005000141__31122024__56155d1c.xlsx
│   │   │   │   ├── ARMOR_20.05.2024__padrao_6__38154005000141__31122023__0286849f.xlsx
│   │   │   │   └── ARMOS_07062023__padrao_4__38154005000141__31122022__5d33bd0f.xlsx
│   │   │   ├── 38183972000131__MASSARI/
│   │   │   │   └── MASSARI_13.06.2024__padrao_6__38183972000131__31122023__289bcfd5.xlsx
│   │   │   ├── 39237248000106__PONTOON_CONV_SE/
│   │   │   │   └── PONTOON_29_08_2024__padrao_3__39237248000106__31122023__1bbe5304.xlsx
│   │   │   ├── 39237248000106__PONTOON_ENERGIA/
│   │   │   │   └── PONTOON 10072025__padrao_3__39237248000106__31122024__7046e5c8.xlsx
│   │   │   ├── 39608949000104__QAIR_COMERCIALIZACAO/
│   │   │   │   ├── QAIR BRASIL (iniciante)_10_10_22__padrao_2__39608949000104__31122021__987c84a7.xlsx
│   │   │   │   └── QAIR_13.06.2024__padrao_6__39608949000104__31122023__2c3c16ba.xlsx
│   │   │   ├── 39702802000189__VOLTALIA_COM/
│   │   │   │   └── SOL SERRA DO MEL III SPE S.A_20.05.2024__padrao_3__39702802000189__31122023__544afe6b.xlsx
│   │   │   ├── 39881421000104__CEEE-G/
│   │   │   │   └── CEEE 14042026__padrao_6__39881421000104__31122024__b26e5045.xlsx
│   │   │   ├── 39953546000100__COMEL/
│   │   │   │   ├── COMEL 18062025__padrao_3__39953546000100__31122024__51265a1d.xlsx
│   │   │   │   └── COMEL_2023__padrao_3__39953546000100__31122023__c4e1ec85.xlsx
│   │   │   ├── 40382949000118__DANSKE_COM/
│   │   │   │   ├── DANSKE 10072025__padrao_3__40382949000118__31122024__f6af2052.xlsx
│   │   │   │   ├── DANSKE 12112024__padrao_6__40382949000118__31122023__09f12f88.xlsx
│   │   │   │   ├── DANSKE 27032026__padrao_6__40382949000118__31122024__90e63584.xlsx
│   │   │   │   └── DANSKE 30072026__padrao_6__40382949000118__31122025__71de7011.xlsx
│   │   │   ├── 41501877000143__SOLAR_BR_COM/
│   │   │   │   └── SOLAR ENERGIA RATING COM 13012026__padrao_6__41501877000143__31122024__fd47bb24.xlsx
│   │   │   ├── 41675130000101__ASOLO2/
│   │   │   │   └── ASOLO 29052026__padrao_6__41675130000101__31122025__21a8f211.xlsx
│   │   │   ├── 41806999000148__LTS_CONV/
│   │   │   │   └── LOTUS_13.06.2024__padrao_6__41806999000148__31122023__3c0abe1e.xlsx
│   │   │   ├── 41808680000151__SKER_COM/
│   │   │   │   ├── STATKRAFT 13082026__padrao_6__41808680000151__31122025__494619dd.xlsx
│   │   │   │   └── STATKRAFT INVESTIMENTOS 29092025__padrao_3__41808680000151__31122024__1a3ba0cd.xlsx
│   │   │   ├── 42102025000146__COPREL_COM/
│   │   │   │   └── COPPREL 16062026__padrao_6__42102025000146__31122025__4219c92b.xlsx
│   │   │   ├── 42126753000198__GAP_ENERGIA/
│   │   │   │   └── GALP ENERGIA 10_11_2022__padrao_2__42126753000198__31122021__75568a79.xlsx
│   │   │   ├── 42311687000126__ENGEFORM_COM/
│   │   │   │   └── ENGEFORM 25062026__padrao_6__42311687000126__31122025__9f93cf8c.xlsx
│   │   │   ├── 42823087000147__NEWAVE/
│   │   │   │   ├── NEWAVE 15042024__padrao_6__42823087000147__31122023__9d1b48e1.xlsx
│   │   │   │   └── NEWAVE_2024__padrao_3__42823087000147__31122024__75265778.xlsx
│   │   │   ├── 42902392000124__SPIC_BRASIL_C/
│   │   │   │   ├── SPIC BRASIL C 13112024__padrao_3__42902392000124__31122023__6a1e7d96.xlsx
│   │   │   │   └── SPIC COM 27062025__padrao_3__42902392000124__31122024__81227e61.xlsx
│   │   │   ├── 42902392000124__SPIC_BRASIL_COM/
│   │   │   │   └── SPIC 13072026__padrao_6__42902392000124__31122025__f3959099.xlsx
│   │   │   ├── 43308969000137__VITOL_POWER/
│   │   │   │   ├── Vitol 04062025__padrao_3__43308969000137__31122024__d830b369.xlsx
│   │   │   │   ├── VITOL 05062026__padrao_6__43308969000137__31122025__4b3aad48.xlsx
│   │   │   │   ├── Vitol 27032026 df 2025__padrao_6__43308969000137__31122024__dabf5ea1.xlsx
│   │   │   │   ├── VITOL 30 04 2024__padrao_6__43308969000137__31122023__7668c33e.xlsx
│   │   │   │   ├── VITOL POWER 20072026__padrao_6__43308969000137__31122025__af212072.xlsx
│   │   │   │   └── Vitol Power Brasil__padrao_2__43308969000137__30062022__e7dc85e6.xlsx
│   │   │   ├── 43344428000164__LIVEN/
│   │   │   │   ├── LIVEN 22042026__padrao_6__43344428000164__31122025__eb2cb353.xlsx
│   │   │   │   └── LIVEN COM 17092025__padrao_3__43344428000164__31122024__a8970887.xlsx
│   │   │   ├── 43412008000178__AES_COMERCIALIZADORA/
│   │   │   │   ├── AES_05012024__padrao_3__43412008000178__31122022__7a4ec190.xlsx
│   │   │   │   └── AES_19.06.2024__padrao_3__43412008000178__31122023__bb3ce3d9.xlsx
│   │   │   ├── 45829681000133__PACIFICO_COMERCIALIZADORA/
│   │   │   │   ├── PACIFICO 18032024__padrao_6__45829681000133__31122023__000231e2.xlsx
│   │   │   │   └── PACIFICO_10062023__padrao_3__45829681000133__31122022__2a5871f6.xlsx
│   │   │   ├── 45836050000141__D3_TRADING/
│   │   │   │   └── D3 Comercializadora_18.03.2024__padrao_6__45836050000141__31122023__f8b9b1a3.xlsx
│   │   │   ├── 46494301000110__TRIA/
│   │   │   │   ├── TRIA 04082026__padrao_6__46494301000110__31122025__d9003dbf.xlsx
│   │   │   │   ├── TRIA 22052025__padrao_3__46494301000110__31122024__8af98af7.xlsx
│   │   │   │   ├── TRIA 27032026 df 2024__padrao_6__46494301000110__31122024__3f680707.xlsx
│   │   │   │   ├── TRIA RATING 28102025__padrao_6__46494301000110__31122024__6172d0c3.xlsx
│   │   │   │   └── TRIA_03.06.2024__padrao_6__46494301000110__31122023__88020709.xlsx
│   │   │   ├── 48251703000119__PAECOM/
│   │   │   │   ├── PAECOM 29052026__padrao_6__48251703000119__31122024__c1325cbb.xlsx
│   │   │   │   └── PANENERGY 05042024__padrao_3__48251703000119__31122023__00ad2d39.xlsx
│   │   │   ├── 48400908000119__BTG_PACTUAL_ENERGIA/
│   │   │   │   └── BTG_29.07.2024__padrao_3__48400908000119__31122023__8ddb7a31.xlsx
│   │   │   ├── 48563988000123__CGN_BRASIL/
│   │   │   │   ├── CGN_30.07.2024__padrao_3__48563988000123__31122023__7ef814a5.xlsx
│   │   │   │   └── CGN_30102023__padrao_3__48563988000123__31122022__63914819.xlsx
│   │   │   ├── 48563988000123__CGN_COMERCIALIZADORA/
│   │   │   │   ├── CGN 05122025__padrao_6__48563988000123__31122024__94044130.xlsx
│   │   │   │   └── CGN Brasil 11082026__padrao_6__48563988000123__31122025__564ed557.xlsx
│   │   │   ├── 48591179000125__SEMPER/
│   │   │   │   ├── SEMPER 02062026__padrao_6__48591179000125__31122025__07da5258.xlsx
│   │   │   │   └── Semper_2024__padrao_3__48591179000125__31122024__4b0b08a6.xlsx
│   │   │   ├── 49983274000137__TC/
│   │   │   │   └── TCCOM_18032024__padrao_6__49983274000137__31122023__519e4286.xlsx
│   │   │   ├── 50729198000117__TRIEX_ENERGIA/
│   │   │   │   └── TRIEX 26032026__padrao_6__50729198000117__31122025__f7bad3da.xlsx
│   │   │   ├── 52177777000120__EGS/
│   │   │   │   └── EGS_29_08_2024__padrao_3__52177777000120__31122023__4d3964b7.xlsx
│   │   │   ├── 53012414000105__JSAFRA/
│   │   │   │   ├── JSAFRA 15072026__padrao_6__53012414000105__31122025__df1455e9.xlsx
│   │   │   │   └── SAFRA 10072025__padrao_3__53012414000105__31122024__d0da1e45.xlsx
│   │   │   ├── 54252354000152__NEC_GERA/
│   │   │   │   ├── NEC ENERGIA 06072026__padrao_6__54252354000152__31122025__9e0e163e.xlsx
│   │   │   │   └── NEC GERACAO 18082026__padrao_6__54252354000152__31122025__23ace549.xlsx
│   │   │   ├── 55935046000194__URUCUIA_GERAÇÃO/
│   │   │   │   └── URUCUIA 23062026__padrao_6__55935046000194__31122025__6e006204.xlsx
│   │   │   ├── 58177643000195__COMERC/
│   │   │   │   ├── COMERC 13_06_2022__padrao_2__58177643000195__31122021__66afcfeb.xlsx
│   │   │   │   └── COMERC_19062023__padrao_3__58177643000195__31122022__a1a6e8ff.xlsx
│   │   │   ├── 76108349003200__CASTROLANDA_COM/
│   │   │   │   ├── CASTROLANDA 01042024__padrao_3__76108349003200__31122023__50e10cc9.xlsx
│   │   │   │   └── CASTROLANDA 10122025__padrao_6__76108349003200__31122024__04318565.xlsx
│   │   │   ├── 76879295000180__PCH_CERCAR/
│   │   │   │   └── CERCAR SA RATING 12022026__padrao_6__76879295000180__31122024__db7b89df.xlsx
│   │   │   └── 85235430000145__COTESA/
│   │   │       ├── COTESA 30_05_2022__padrao_2__85235430000145__31122021__5f70d8ba.xlsx
│   │   │       └── COTESA_14_10_2021__padrao_2__85235430000145__31122020__c6c551ed.xlsx
│   │   ├── fichas_consumidores_raw/
│   │   │   ├── 00001180000126__CENTRAIS_ELETRICAS_BRASILEIRAS_SA_ELETROBRAS/
│   │   │   │   └── Eletrobras_30052025__padrao_1__00001180000126__31122024__8cd5a9f3.xlsx
│   │   │   ├── 00021096000417__THE_LYCRA_COMPANY_INDUSTRIA_E_COMERCIO_TÊXTIL_LTDA/
│   │   │   │   └── LYCRA_22062023__padrao_1__00021096000417__31122021__8c3a4c60.xlsx
│   │   │   ├── 00074569000100__RIO_DE_JANEIRO_REFRESCOS_LTDA/
│   │   │   │   ├── Rio de Janeiro Refrescos - Avaliação Mid__padrao_1__00074569000100__31122021__3c6016d4.xlsx
│   │   │   │   └── Rio de Janeiro Refrescos 16102023__padrao_1__00074569000100__31122022__6b0a9e01.xlsx
│   │   │   ├── 00080671000100__CARAMURU_ALIMENTOS_S.A/
│   │   │   │   └── Caramuru 2022-07-18__padrao_1__00080671000100__31122021__0202636e.xlsx
│   │   │   ├── 00082024000137__COMPANHIA_DE_SANEAMENTO_AMBIENTAL_DO_DISTRITO_FEDERAL/
│   │   │   │   └── CAESB RATING 20012026__padrao_2__00082024000137__31122024__af170b8a.xlsx
│   │   │   ├── 00291633000104__DOIS_MARCOS_SEMENTES_LTDA/
│   │   │   │   └── Dois Marcos Sementes 03042024__padrao_1__00291633000104__31122022__019386a7.xlsx
│   │   │   ├── 00529188000160__LATICINIOS_RUHBAN_LTDA/
│   │   │   │   └── Laticínios Ruhban 09102025__padrao_2__00529188000160__125bd4ef.xlsx
│   │   │   ├── 00767144000178__-129478/
│   │   │   │   └── AHLSTROM-MUNKSJO 27052026__padrao_2__00767144000178__31122025__dfe0ef31.xlsx
│   │   │   ├── 00771979000100__BALL_DO_BRASIL_LTDA/
│   │   │   │   └── BALL_02032023__padrao_1__00771979000100__31122021__ad9e787e.xlsx
│   │   │   ├── 00831373000104__LOUIS_DREYFUS_COMPANY_SUCOS_S.A/
│   │   │   │   ├── LDC SUCOS 06052026__padrao_2__00831373000104__31122025__3abde46b.xlsx
│   │   │   │   └── LDC SUCOS 30062025__padrao_1__00831373000104__31122024__4033bbcd.xlsx
│   │   │   ├── 00990842000138__ACO_CEARENSE_INDUSTRIAL_LTDA/
│   │   │   │   └── ACO CEARENSE RATING 07012026__padrao_2__00990842000138__31122024__c42f0857.xlsx
│   │   │   ├── 01105558000102__WD_AGROINDUSTRIAL_LTDA/
│   │   │   │   └── WD AGROINDUSTRIAL 20052026__padrao_2__01105558000102__31122024__99b02258.xlsx
│   │   │   ├── 01144673000188__ENGETECH_COMERCIO_E_INDUSTRIA_DE_PLASTICOS_LTDA/
│   │   │   │   └── Engetech 10032025__padrao_1__01144673000188__31122024__11be1112.xlsx
│   │   │   ├── 01261681000104__WHB_AUTOMOTIVE_S.A/
│   │   │   │   ├── WHB_08042024__padrao_1__01261681000104__31122022__f0b4f6fc.xlsx
│   │   │   │   └── WHB_11042024__padrao_1__01261681000104__31122023__c7d56488.xlsx
│   │   │   ├── 01317277000105__PORTO_DE_ITAPOA/
│   │   │   │   └── PORTO ITAPOA RATING 10122025__padrao_2__01317277000105__31122024__acb727aa.xlsx
│   │   │   ├── 01325023000139__CERÂMICA_FORMIGRES/
│   │   │   │   └── Ceramica_Formigres_18_01_2022__padrao_1__01325023000139__31122020__fb96e543.xlsx
│   │   │   ├── 01333984000195__SEGALAS_ALIMENTOS_LTDA/
│   │   │   │   └── Segalas Alimentos - Avaliação Middle__padrao_1__01333984000195__31122021__90931f64.xlsx
│   │   │   ├── 01599436000101__AMSTED-MAXION_FUNDICAO_E_EQUIPAMENTOS_FERROVIARIOS_S_A/
│   │   │   │   └── FICHA_CONSUMIDORES_AMSTED_MAXXION_PREENC__padrao_3__01599436000101__31082025__bb93f28f.xlsx
│   │   │   ├── 01615814000101__UNILEVER_BRASIL_INDUSTRIAL_LTDA/
│   │   │   │   └── Unilever_17112023__padrao_1__01615814000101__31122022__7f7e312d.xlsx
│   │   │   ├── 01616929000102__SANEAMENTO_DE_GOIAS_S_A/
│   │   │   │   └── SANEAGO_20250106__padrao_1__01616929000102__31122023__2aa099e7.xlsx
│   │   │   ├── 01621399000190__OGGI_SORVETES_LTDA/
│   │   │   │   └── Oggi Alimentos_13_10_2022__padrao_1__01621399000190__31122022__70a7fe9a.xlsx
│   │   │   ├── 01637895000132__VOTORANTIM_CIMENTOS_S.A/
│   │   │   │   ├── VOTORANTIM SA 11052026__padrao_2__01637895000132__31122025__6f4f4ac1.xlsx
│   │   │   │   └── Votorantim__padrao_1__01637895000132__31122021__5faaff79.xlsx
│   │   │   ├── 01682147000171__AVENORTE_AVICOLA_CIANORTE_LTDA/
│   │   │   │   ├── AVENORTE_20092023__padrao_1__01682147000171__31122023__f4cdd710.xlsx
│   │   │   │   └── AVENORTE_30062023__padrao_1__01682147000171__31122022__c60f6f10.xlsx
│   │   │   ├── 01832301000144__VIAÇÃO_CAMPO_BELO_LTDA/
│   │   │   │   └── CAMPO BELO G1 CARLOS CALDEIRA 30072026__padrao_3__01832301000144__31122025__7b724c22.xlsx
│   │   │   ├── 01838723000127__BRF_S.A/
│   │   │   │   ├── BRF 12082024__padrao_1__01838723000127__31122023__a525427f.xlsx
│   │   │   │   ├── BRF FOODS 22072025__padrao_1__01838723000127__31122024__b2de4d00.xlsx
│   │   │   │   └── BRF RATING 01122025__padrao_2__01838723000127__31122025__73f5155c.xlsx
│   │   │   ├── 01961898000127__CARGILL_ALIMENTOS_LTDA/
│   │   │   │   ├── Cargil 05.08.2024__padrao_1__01961898000127__31122023__026482d6.xlsx
│   │   │   │   └── Cargil 28022024__padrao_1__01961898000127__31122022__9733cb32.xlsx
│   │   │   ├── 02036483000614__CONTINENTAL_AG/
│   │   │   │   └── CONTINENTAL_15072024_V1__padrao_1__02036483000614__31122023__01eb0779.xlsx
│   │   │   ├── 02036483000614__CONTINENTAL_DO_BRASIL_PRODUTOS_AUTOMOTIVOS_LTDA/
│   │   │   │   └── Continental Camaçari_21_02_2022__padrao_1__02036483000614__31122020__f3e60e98.xlsx
│   │   │   ├── 02041460000193__V.TAL_-_REDE_NEUTRA_DE_TELECOMUNICACOES_S.A/
│   │   │   │   └── V.TAL RATING 31102025__padrao_2__02041460000193__31122024__ceef233e.xlsx
│   │   │   ├── 02290277000121__CNEP_-_CADASTRO_NACIONAL_DE_EMPRESAS_PUNIDAS/
│   │   │   │   └── Kimberly-Clark análises__padrao_1__02290277000121__31122021__8efa8360.xlsx
│   │   │   ├── 02326750000183__INTERCAST_S_A/
│   │   │   │   └── Intercast - Avaliação Middle__padrao_1__02326750000183__31122021__02d75fb7.xlsx
│   │   │   ├── 02341494000101__NORFIL_S_A_INDUSTRIA_TEXTIL/
│   │   │   │   ├── NORFIL 13062025__padrao_1__02341494000101__31122024__6022f1e6.xlsx
│   │   │   │   ├── NORFIL 15022024__padrao_1__02341494000101__31122022__7ed2fd25.xlsx
│   │   │   │   └── NORFIL SA 27042026__padrao_2__02341494000101__31122025__d74bd54d.xlsx
│   │   │   ├── 02341494000101__NORFIL_S_A_INDÚSTRIA_TÊXTIL/
│   │   │   │   └── NORFIL_13_01_23__padrao_1__02341494000101__31122021__0dab96d4.xlsx
│   │   │   ├── 02357659000125__ELIZABETH_PORCELANATO_S_A/
│   │   │   │   └── Elizabeth Porcelanato__padrao_1__02357659000125__31122021__efb2f4c5.xlsx
│   │   │   ├── 02359572000430__ANGLO_AMERICAN_MINERIO_DE_FERRO_BRASIL_S_A/
│   │   │   │   ├── Anglo Amercia 27022024__padrao_1__02359572000430__31122022__640fff72.xlsx
│   │   │   │   └── ANGLO AMERICAN RATING 14102025__padrao_2__02359572000430__31122024__14c44b45.xlsx
│   │   │   ├── 02421421000111__TIM_S_A/
│   │   │   │   └── TIM - Avaliação Middle__padrao_1__02421421000111__31122021__1862aeb4.xlsx
│   │   │   ├── 02429732000127__TERPHANE_LTDA/
│   │   │   │   ├── Terphane - Avaliação Middle__padrao_1__02429732000127__31122021__7e289507.xlsx
│   │   │   │   └── TERPHANE RATING 30012026__padrao_2__02429732000127__31122024__18b44cd7.xlsx
│   │   │   ├── 02709449000159__PETROBRAS_TRANSPORTE_S.A_-_TRANSPETRO/
│   │   │   │   ├── TRANSPETRO 08062026__padrao_3__02709449000159__31122025__b100b981.xlsx
│   │   │   │   └── TRANSPETRO 09072025__padrao_1__02709449000159__31122024__d86cfd1c.xlsx
│   │   │   ├── 02740510000120__VEOLIA_ENERGIA_BRASIL_LTDA/
│   │   │   │   └── VEOLIA_28082024__padrao_1__02740510000120__31122023__d15f1da6.xlsx
│   │   │   ├── 02846056000197__CCR_S.A/
│   │   │   │   └── Metro Bahia 18042024__padrao_1__02846056000197__31122023__614256c5.xlsx
│   │   │   ├── 02846056000197__MOTIVA_INFRAESTRUTURA_DE_MOBILIDADE_S.A/
│   │   │   │   ├── MOTIVA RATING 25102025__padrao_2__02846056000197__31122024__b645cb18.xlsx
│   │   │   │   └── MOTIVA SA 13082026__padrao_3__02846056000197__31122025__b75f3e0e.xlsx
│   │   │   ├── 02850990000182__CENTRO_EDUCACIONAL_ALVES_FARIA_LTDA/
│   │   │   │   └── FACULDADES ALFA RATING 29102025__padrao_2__02850990000182__31122024__29e60c20.xlsx
│   │   │   ├── 02916265000160__JBS_S_A/
│   │   │   │   ├── JBS 11012024__padrao_1__02916265000160__31122022__d0764404.xlsx
│   │   │   │   ├── JBS 13052026__padrao_2__02916265000160__31122025__99adab02.xlsx
│   │   │   │   └── JBS SA - 08072025__padrao_1__02916265000160__31122024__076745bf.xlsx
│   │   │   ├── 02916265037322__JBS_S_A/
│   │   │   │   └── JBSFILIAL_01102024__padrao_1__02916265037322__31122023__7fdf951b.xlsx
│   │   │   ├── 03206039000158__VITOPEL_DO_BRASIL_LTDA/
│   │   │   │   └── Vitopel_2023_07_27__padrao_1__03206039000158__31122021__68c4a33e.xlsx
│   │   │   ├── 03327149000178__UNIRON_-_UNIAO_DAS_ESCOLAS_SUPERIORES_DE_RONDONIA_LTDA/
│   │   │   │   └── UNIRON_10_10_2022__padrao_1__03327149000178__31122021__0c10ed88.xlsx
│   │   │   ├── 03327988000196__LHG_MINING_CORUMBA_S.A/
│   │   │   │   └── MINING CORUMBA RATING 28012026__padrao_2__03327988000196__31122024__93cf26fa.xlsx
│   │   │   ├── 03342704000130__PETRORECONCAVO_S_A/
│   │   │   │   ├── PETRORECONCAVO 08052026__padrao_2__03342704000130__31122025__5bcecadf.xlsx
│   │   │   │   └── PETRORECONCAVO RATING 11112025__padrao_2__03342704000130__31122024__411c3381.xlsx
│   │   │   ├── 03407049000151__VOTORANTIM_S.A/
│   │   │   │   ├── VOTORANTIM 07072025__padrao_1__03407049000151__31122024__939cc975.xlsx
│   │   │   │   └── VOTORANTIM 07072026__padrao_3__03407049000151__31122025__c57d0810.xlsx
│   │   │   ├── 03503798000182__AGRO_NORTE_PESQUISA_E_SEMENTES_LTDA/
│   │   │   │   └── AGRONORTE RATING 02032026__padrao_2__03503798000182__31122024__9aa0e395.xlsx
│   │   │   ├── 03509978000171__FACCHINI_S_A/
│   │   │   │   ├── FACCHINI SA 22122025__padrao_2__03509978000171__31122024__eee64e6a.xlsx
│   │   │   │   └── FACCHINI_20022025__padrao_1__03509978000171__31122023__1eb8d855.xlsx
│   │   │   ├── 03582243000173__DAE_SA_-_AGUA_E_ESGOTO/
│   │   │   │   └── DAE SA AGUA E ESGOTO 18082023__padrao_1__03582243000173__31122022__87a745d7.xlsx
│   │   │   ├── 03650060000148__EMPRESA_MARANHENSE_DE_ADMINISTRACAO_PORTUARIA_-_EMAP/
│   │   │   │   └── CONTINENTAL_15072024__padrao_1__03650060000148__31122023__05cff9a8.xlsx
│   │   │   ├── 03816532000190__COLGATE_PALMOLIVE_INDUSTRIAL_LTDA/
│   │   │   │   └── COLGATE 24042025__padrao_1__03816532000190__31122024__2062e4f2.xlsx
│   │   │   ├── 03853896000140__MARFRIG_GLOBAL_FOODS_S.A/
│   │   │   │   ├── MARFRIG RATING 05112025__padrao_2__03853896000140__31122024__65733912.xlsx
│   │   │   │   └── MBRF_09062026__padrao_3__03853896000140__31122025__a261f1c9.xlsx
│   │   │   ├── 04027894000164__DUPATRI_HOSPITALAR_COMERCIO,_IMPORTACAO_E_EXPORTACAO_LTDA/
│   │   │   │   └── DUPATRI HOSPITALAR__padrao_2__04027894000164__31122025__fae6571e.xlsx
│   │   │   ├── 04176791000247__FIBRAPLAC_PAINEIS_DE_MADEIRA_LTDA/
│   │   │   │   └── FIBRAPLAC_12_08_2024__padrao_1__04176791000247__31122023__10dc7351.xlsx
│   │   │   ├── 04201168000116__LUME_CERAMICA_LTDA/
│   │   │   │   └── LUME CERAMICA 14042026__padrao_2__04201168000116__31122024__b5cc3f5f.xlsx
│   │   │   ├── 04426411000102__ENERPEIXE_S.A/
│   │   │   │   └── ENERPEIXE 15092025__padrao_1__04426411000102__31122024__fb5ffb44.xlsx
│   │   │   ├── 04558449000392__GLOBALPACK_INDUSTRIA_E_COMERCIO_LTDA/
│   │   │   │   └── Globalpack 17012024__padrao_1__04558449000392__31122022__47406b36.xlsx
│   │   │   ├── 04630268000168__SERLONAS_INDUSTRIA_E_COMERCIO_DE_PLASTICOS_LTDA/
│   │   │   │   └── SERLONAS RATING 10032026__padrao_2__04630268000168__31122025__a1dd608f.xlsx
│   │   │   ├── 04865228000103__DAUS_INDUSTRIA_DE_ALIMENTOS_S.A/
│   │   │   │   └── DAUS ALIMENTOS RATING 16032026__padrao_2__04865228000103__31122025__b8075dc5.xlsx
│   │   │   ├── 04932216000146__MINERACAO_RIO_DO_NORTE_SA/
│   │   │   │   ├── MINERACAO RIO DO NORTE 16062026__padrao_3__04932216000146__31122025__82bf6ca2.xlsx
│   │   │   │   └── MINERACAO RIO DO NORTE SA__padrao_2__04932216000146__31122024__ee094deb.xlsx
│   │   │   ├── 05053020000144__ALBRAS_ALUMINIO_BRASILEIRO_S_A/
│   │   │   │   ├── ALBRAS 21072026__padrao_3__05053020000144__31122025__793114a9.xlsx
│   │   │   │   └── ALBRAS 27052025__padrao_1__05053020000144__31122024__562665da.xlsx
│   │   │   ├── 05054671000159__LIDER_COMERCIO_E_INDUSTRIA_LTDA/
│   │   │   │   ├── GRUPO LIDER RATING 11122025__padrao_2__05054671000159__31122024__de54ce01.xlsx
│   │   │   │   └── LÍDER (Atacadista) 02122024__padrao_1__05054671000159__31122023__70b723d0.xlsx
│   │   │   ├── 05126928000130__DULCE_ACQUA_MINERALE_DISTRIBUIDORA_LTDA/
│   │   │   │   └── Dulce Acqua_28_09_2022__padrao_1__05126928000130__31122021__386efd09.xlsx
│   │   │   ├── 05251919000171__METALBRAZING_BRASAGEM_E_TRATAMENTO_TERMICO_LTDA/
│   │   │   │   └── METALBRAZING 11062026__padrao_3__05251919000171__31122025__545f8f43.xlsx
│   │   │   ├── 05297665000122__FIACAO_ALLIANCE_LTDA/
│   │   │   │   └── ALLIANCE RATING 04022025__padrao_2__05297665000122__31122025__472e95b7.xlsx
│   │   │   ├── 05620523000154__ATVOS_BIOENERGIA_ELDORADO_S.A/
│   │   │   │   └── ATVOS BIOENERGIA ELDORADO RATING 2212202__padrao_2__05620523000154__31032025__614031e7.xlsx
│   │   │   ├── 05798883000140__SUPREMO_CIMENTOS_S.A/
│   │   │   │   └── Supremo Cimentos_02032023__padrao_1__05798883000140__31122021__e33a0665.xlsx
│   │   │   ├── 05848387000154__ALUNORTE_ALUMINA_DO_NORTE_DO_BRASIL_S_A/
│   │   │   │   ├── ALUNORTE 17062026__padrao_3__05848387000154__31122025__9a710d26.xlsx
│   │   │   │   └── ALUNORTE RATING 18122025__padrao_2__05848387000154__31122024__27be07f2.xlsx
│   │   │   ├── 05878397000132__ALIANSCE_SONAE_SHOPPING_CENTERS_S.A/
│   │   │   │   └── ALIANSCE SONAE_29062023__padrao_1__05878397000132__31122022__5cd43bc6.xlsx
│   │   │   ├── 06047087000139__REDE_D'OR_SAO_LUIZ_S.A/
│   │   │   │   └── REDE DOR SÃO LUIZ__padrao_1__06047087000139__31122021__9a3185e5.xlsx
│   │   │   ├── 06057223000171__SENDAS_DISTRIBUIDORA_S_A/
│   │   │   │   ├── ASSAI ATACADISTA 25.07.2024__padrao_1__06057223000171__31122023__5f4444b1.xlsx
│   │   │   │   ├── ASSAI RATING 09032026__padrao_2__06057223000171__31122025__f92a308e.xlsx
│   │   │   │   ├── Assaí atacadista 25032025__padrao_1__06057223000171__31122024__be9cf5ba.xlsx
│   │   │   │   ├── Assaí Atacadista_24072023__padrao_1__06057223000171__31122022__d186ca09.xlsx
│   │   │   │   └── SENDAS DISTRIBUIDORA 22_08_2022__padrao_1__06057223000171__31122021__8bd1bbc1.xlsx
│   │   │   ├── 06164824000183__M.H.C._PLASTICOS_LTDA/
│   │   │   │   └── MHC PLASTICOS 28072025__padrao_1__06164824000183__31122024__43f3c356.xlsx
│   │   │   ├── 06164824000183__M.H.C._PLASTICOS_LTDA_EM_RECUPERACAO_JUDICIAL/
│   │   │   │   └── FICHA MODELO ddmmaaaa__padrao_1__06164824000183__31122023__e143673a.xlsx
│   │   │   ├── 06268099000193__TRANSPPASS_TRANSPORTE_DE_PASSAGEIROS_LTDA/
│   │   │   │   └── TRANSPPASS 03082026__padrao_3__06268099000193__31122025__5da752c3.xlsx
│   │   │   ├── 06315338000119__COFCO_INTERNATIONAL_BRASIL_S.A/
│   │   │   │   ├── COFCO 16042026__padrao_2__06315338000119__31122024__d8eec9e7.xlsx
│   │   │   │   └── COFCO 21072026__padrao_3__06315338000119__31122025__047ef85e.xlsx
│   │   │   ├── 06886749000407__HUBNER_COMPONENTES_E_SISTEMAS_AUTOMOTIVOS_S_A/
│   │   │   │   └── HUBNER 19022024__padrao_1__06886749000407__31122022__43f424fd.xlsx
│   │   │   ├── 07005330000119__TERNIUM_BRASIL_LTDA/
│   │   │   │   ├── TERNIUM 26052026__padrao_2__07005330000119__31122025__c7268245.xlsx
│   │   │   │   └── TERNIUM BRASIL 02072025__padrao_1__07005330000119__31122024__3a057aa1.xlsx
│   │   │   ├── 07037123000146__ECOURBIS_AMBIENTAL_S.A/
│   │   │   │   └── ECOURBIS - 17062026__padrao_3__07037123000146__31122025__6de8ad5c.xlsx
│   │   │   ├── 07094315000194__CRIUVA_ENERGETICA_S_A/
│   │   │   │   └── CRIUVA ENERGETICA 12062025__padrao_1__07094315000194__31122024__8b4c74df.xlsx
│   │   │   ├── 07094597000120__SERRANA_ENERGETICA_S_A/
│   │   │   │   └── SERRANA 11062025__padrao_1__07094597000120__31122024__d3346017.xlsx
│   │   │   ├── 07175725000160__WEG_EQUIPAMENTOS_ELETRICOS_S.A/
│   │   │   │   └── WEG 11012024__padrao_1__07175725000160__31122022__052f2a15.xlsx
│   │   │   ├── 07175725000160__WEG_EQUIPAMENTOS_ELETRICOS_S_A/
│   │   │   │   ├── WEG - MATRIZ 15052026__padrao_2__07175725000160__31122025__c92634c5.xlsx
│   │   │   │   ├── WEG 03072025__padrao_1__07175725000160__31122024__90d97390.xlsx
│   │   │   │   └── WEG 25112024__padrao_1__07175725000160__31122023__7ddd0920.xlsx
│   │   │   ├── 07206816000115__M_DIAS_BRANCO_S.A._INDUSTRIA_E_COMERCIO_DE_ALIMENTOS/
│   │   │   │   ├── M DIAS BRANCO 08062026__padrao_3__07206816000115__31122025__aa03fa61.xlsx
│   │   │   │   └── M DIAS BRANCO 15082025__padrao_1__07206816000115__31122024__2908e2ca.xlsx
│   │   │   ├── 07226794000155__COMPANHIA_AGUAS_DE_JOINVILLE/
│   │   │   │   └── Companhia Aguas de Joinville - Avaliação__padrao_1__07226794000155__31122021__0b1be501.xlsx
│   │   │   ├── 07227026000116__CENTRALPACK_EMBALAGENS_LTDA/
│   │   │   │   └── CENTRAL PACK 24082023__padrao_1__07227026000116__31122022__7f6022a2.xlsx
│   │   │   ├── 07255463000143__SUPER_LIS_SUPERMERCADO_LTDA/
│   │   │   │   └── SUPERMERCADO LIS RATING 29012026__padrao_2__07255463000143__31122024__cbac6982.xlsx
│   │   │   ├── 07280328001804__IPIRANGA_AGROINDUSTRIAL_S.A/
│   │   │   │   └── IPIRANGA AGROINDUSTRIAL 0605026__padrao_2__07280328001804__31032025__8327a90c.xlsx
│   │   │   ├── 07298800000180__ATVOS_BIOENERGIA_CONQUISTA_DO_PONTAL_S.A/
│   │   │   │   └── ATVOS BIOENERGIA CONQUISTA DO PONTAL RAT__padrao_2__07298800000180__31032025__ef630b1e.xlsx
│   │   │   ├── 07322382000119__BE8_S.A/
│   │   │   │   ├── BE8 RATING 11122025__padrao_2__07322382000119__31122024__77452d9c.xlsx
│   │   │   │   └── BE8_26_08_2024__padrao_1__07322382000119__31122023__04773119.xlsx
│   │   │   ├── 07358761000169__GERDAU_ACOS_LONGOS_S.A/
│   │   │   │   ├── GERDAU Aços Longos 11122024__padrao_1__07358761000169__31122023__db3be5db.xlsx
│   │   │   │   ├── GERDAU AÇOS LONGOS 13062025__padrao_1__07358761000169__31122024__f9069969.xlsx
│   │   │   │   └── GERDAU AÇOS LONGOS RATING 15102025__padrao_2__07358761000169__e381b84b.xlsx
│   │   │   ├── 07358761005632__GERDAU_ACOS_LONGOS_S.A/
│   │   │   │   └── GERDAU ACOS LONGOS - 00482085__padrao_2__07358761005632__31122025__c8604bb3.xlsx
│   │   │   ├── 07404052000172__CRUZ_VERMELHA_BRASILEIRA_-_FILIAL_DO_ESTADO_DO_PARANA/
│   │   │   │   └── Hospital Cruz Vermelha - Avaliação Middl__padrao_1__07404052000172__31122021__329e42d8.xlsx
│   │   │   ├── 07450031000193__204-6_-_SOCIEDADE_ANÔNIMA_ABERTA/
│   │   │   │   └── CJ DO BRASIL 01072026__padrao_3__07450031000193__31122025__58cc677f.xlsx
│   │   │   ├── 07450031000193__CNEP_-_CADASTRO_NACIONAL_DE_EMPRESAS_PUNIDAS/
│   │   │   │   └── CJ do Brasil_13042023__padrao_1__07450031000193__31122021__5be760b6.xlsx
│   │   │   ├── 07632665000167__B.O_PAPER_BRASIL_IND_DE_PAPEIS_LTDA/
│   │   │   │   └── BOPAPER_2023_05_11__padrao_1__07632665000167__31122022__bbe9d998.xlsx
│   │   │   ├── 07632665000167__B.O_PAPER_BRASIL_INDUSTRIA_DE_PAPEIS_LTDA/
│   │   │   │   ├── BO Paper 04_05_2022__padrao_1__07632665000167__31122021__5bdc5b5e.xlsx
│   │   │   │   └── BO PAPER RATING 13102025__padrao_2__07632665000167__31122024__96df73e7.xlsx
│   │   │   ├── 07632665000167__B.O_PAPER_BRASIL_INDÚSTRIA_DE_PAPÉIS_LTDA/
│   │   │   │   └── BO PAPER 02062026__padrao_2__07632665000167__31122025__f48fa7b7.xlsx
│   │   │   ├── 07647780000105__BOA_FE_ENERGETICA_S_A/
│   │   │   │   └── BOA FÉ ENERGÉTICA 12062025__padrao_1__07647780000105__31122024__16ecdff7.xlsx
│   │   │   ├── 07647793000184__AUTODROMO_ENERGETICA_S_A/
│   │   │   │   └── AUTODROMO ENERGÉTICA 13062025__padrao_1__07647793000184__31122024__bc709411.xlsx
│   │   │   ├── 07682638000107__CONCESSIONARIA_DA_LINHA_4_DO_METRO_DE_SAO_PAULO_S.A/
│   │   │   │   └── LINHA 4 - MOTIVA 06072026__padrao_3__07682638000107__31122025__777060f0.xlsx
│   │   │   ├── 07689002000189__EMBRAER_S.A/
│   │   │   │   ├── EMBRAER 05052026__padrao_2__07689002000189__31122025__ce58c10e.xlsx
│   │   │   │   └── EMBRAER_10042023__padrao_1__07689002000189__31122022__60c03ecf.xlsx
│   │   │   ├── 07705880000140__MADEIREIRA_COSTA_E_PALU_LTDA/
│   │   │   │   └── Costa e Palu 16_08_2022__padrao_1__07705880000140__31122021__84b6e0cf.xlsx
│   │   │   ├── 07718633000189__UNIDASUL_DISTRIBUIDORA_ALIMENTICIA_S_A/
│   │   │   │   └── UNIDAS SUL 180052026__padrao_2__07718633000189__31122025__42427791.xlsx
│   │   │   ├── 07726782000190__SAO_PAULO_ENERGETICA_S_A/
│   │   │   │   └── SÃO PAULO ENERGÉTICA 11062025__padrao_1__07726782000190__31122024__9d099715.xlsx
│   │   │   ├── 07903169000109__ADECOAGRO_VALE_DO_IVINHEMA_S.A/
│   │   │   │   └── ADECOAGRO 10042026__padrao_2__07903169000109__31122025__5961e33e.xlsx
│   │   │   ├── 07933914000154__SIDERURGICA_NORTE_BRASIL_S_A/
│   │   │   │   └── SINOBRAS 09072026__padrao_3__07933914000154__31122025__0a7ed7f4.xlsx
│   │   │   ├── 07957149000102__COMPANHIA_NACIONAL_DE_CIMENTO_-_CNC/
│   │   │   │   └── Cimento Campeão Alvorada_14_01_2022__padrao_1__07957149000102__31122020__7cfb4cce.xlsx
│   │   │   ├── 08070508000178__RAIZEN_ENERGIA_S.A/
│   │   │   │   └── RAIZEN_20092023__padrao_1__08070508000178__31122023__b4f05f90.xlsx
│   │   │   ├── 08070566000100__ATVOS_BIOENERGIA_BRENCO_S.A/
│   │   │   │   └── ATVOS BIOENERGIA BRENCO RATING 22122025__padrao_2__08070566000100__31032025__1fa506bb.xlsx
│   │   │   ├── 08090788000267__BOZEL_BRASIL_S.A/
│   │   │   │   ├── BOZEL 24062026__padrao_3__08090788000267__31122025__c1a69f33.xlsx
│   │   │   │   └── BOZEL BRASIL 21082025__padrao_1__08090788000267__31122024__61615589.xlsx
│   │   │   ├── 08201770000104__BELLO_ALIMENTOS_LTDA/
│   │   │   │   └── BELLO_01062023__padrao_1__08201770000104__31122022__7538c0bf.xlsx
│   │   │   ├── 08334385000135__COMPANHIA_DE_AGUAS_E_ESGOTOS_DO_RIO_GRANDE_DO_NORTE/
│   │   │   │   └── CAERN_23042025__padrao_1__08334385000135__31122024__cc258eef.xlsx
│   │   │   ├── 08405256000190__AMBIENTAL_TRANSPORTES_URBANOS_S_A/
│   │   │   │   └── AMBIENTAL - NESTOR DE BARROS 31072026__padrao_3__08405256000190__31122025__eed6be54.xlsx
│   │   │   ├── 08598391000108__ATVOS_BIOENERGIA_RIO_CLARO_S.A/
│   │   │   │   └── ATVOS BIOENERGIA RIO CLARO RATING 231220__padrao_2__08598391000108__49e65286.xlsx
│   │   │   ├── 08666285000106__QAIR_BRASIL_PARTICIPACOES_S.A/
│   │   │   │   └── QAIR 02072025__padrao_1__08666285000106__31122024__43a3728a.xlsx
│   │   │   ├── 08670308000156__CPIC_BRASIL_FIBRAS_DE_VIDRO_LTDA/
│   │   │   │   └── CPIC 02_02_2023__padrao_1__08670308000156__31122021__01bb84dc.xlsx
│   │   │   ├── 08689024000101__VALLOUREC_SOLUCOES_TUBULARES_DO_BRASIL_S.A/
│   │   │   │   └── VALLOUREC SOLUCOES RATING 08012026__padrao_2__08689024000101__31122024__09ded324.xlsx
│   │   │   ├── 08740765000170__DUPLAS_-_INDUSTRIA_DE_PECAS_PLASTICAS_LTDA/
│   │   │   │   └── DUPLAS RATING 09022026__padrao_2__08740765000170__31122024__e7b309fc.xlsx
│   │   │   ├── 08803452000113__SUDATI_PAINEIS_S.A/
│   │   │   │   └── SUDATI 08042024__padrao_1__08803452000113__31122022__1fb6be36.xlsx
│   │   │   ├── 08827501000158__AEGEA_SANEAMENTO_E_PARTICIPACOES_S.A/
│   │   │   │   ├── AEGEA 20-07-2022__padrao_1__08827501000158__31122021__12dedf77.xlsx
│   │   │   │   └── AEGEA SANEAMENTO 23072026__padrao_3__08827501000158__31032026__75a31198.xlsx
│   │   │   ├── 08902291000115__CSN_MINERACAO_S.A/
│   │   │   │   └── CSN MINERAÇÃO 22082025__padrao_1__08902291000115__31122024__d11c0b73.xlsx
│   │   │   ├── 08903942000191__GAZIT_BRASIL_LTDA/
│   │   │   │   ├── GAZIT 05022024__padrao_1__08903942000191__afceaebd.xlsx
│   │   │   │   └── Grupo GAZIT 10012024__padrao_1__08903942000191__31122022__b4773a4e.xlsx
│   │   │   ├── 08906558000142__ATVOS_BIOENERGIA_SANTA_LUZIA/
│   │   │   │   └── ATVOS BIOENERGIA SANTA LUZIA__padrao_2__08906558000142__31122025__f811a679.xlsx
│   │   │   ├── 08944802000161__CERÂMICA_ELIZABETH_SUL_LTDA/
│   │   │   │   └── CERÂMICA ELISABETH__padrao_1__08944802000161__31122020__610a9852.xlsx
│   │   │   ├── 09053134000145__ELFA_MEDICAMENTOS_S.A/
│   │   │   │   └── ELFA MEDICAMENTOS 22052026__padrao_2__09053134000145__31122025__a81dcd22.xlsx
│   │   │   ├── 09075317000161__H.F.SISTEMAS_DE_FREIO_LTDA/
│   │   │   │   └── HF SISTEMAS DE FREIOS RATING 26012026__padrao_2__09075317000161__31122024__a8228e5a.xlsx
│   │   │   ├── 09258807000101__BRASTEX_S_A/
│   │   │   │   ├── Brastex 10062024__padrao_1__09258807000101__31122023__cf1ecf94.xlsx
│   │   │   │   └── BRASTEX RATING 08012026__padrao_2__09258807000101__31122024__7b1f02c5.xlsx
│   │   │   ├── 09266129000110__SANEAMENTO_AMBIENTAL_AGUAS_DO_BRASIL_S_A/
│   │   │   │   └── GAB 10012024__padrao_1__09266129000110__31122022__0e035133.xlsx
│   │   │   ├── 09341337000137__CENTRAIS_EÓLICAS_DE_CAETITÉ_PARTICIPAÇÕES_S.A/
│   │   │   │   └── Centrais Eólicas de Caetité Participaçõe__padrao_2__09341337000137__31122023__d1aaaba7.xlsx
│   │   │   ├── 09391823000240__SANTO_ANTONIO_ENERGIA_S.A/
│   │   │   │   └── Santo Antonio Energia 01102024__padrao_1__09391823000240__31122023__db767191.xlsx
│   │   │   ├── 09461639000149__GUERRO_&_PAGNUSSAT_LTDA/
│   │   │   │   └── GUERRO 08042024__padrao_1__09461639000149__31122022__d29904a0.xlsx
│   │   │   ├── 09509535000167__ARCELORMITTAL_PECEM_S.A/
│   │   │   │   └── ARCELORMITTAL - 00350481__padrao_1__09509535000167__31122024__4142ab15.xlsx
│   │   │   ├── 09509569000151__COMUSA_-_SERVICOS_DE_AGUA_E_ESGOTO_DE_NOVO_HAMBURGO/
│   │   │   │   └── COMUSA 05072024__padrao_1__09509569000151__31122023__dcc2d01d.xlsx
│   │   │   ├── 10324624000118__CONCESSAO_METROVIARIA_DO_RIO_DE_JANEIRO_S.A/
│   │   │   │   ├── METRO RIO 13082025__padrao_1__10324624000118__31122024__b3d8139e.xlsx
│   │   │   │   ├── METRORIO 30062026__padrao_3__10324624000118__31122025__08975c57.xlsx
│   │   │   │   └── MetroRio_06042023__padrao_1__10324624000118__31122021__03dfd338.xlsx
│   │   │   ├── 10366780000141__CENTRAIS_ELETRICAS_DA_PARAIBA_S.A._-_EPASA/
│   │   │   │   └── EPASA 21122023__padrao_1__10366780000141__31122022__f5ebed0d.xlsx
│   │   │   ├── 10394422000142__HYUNDAI_MOTOR_BRASIL_MONTADORA_DE_AUTOMOVEIS_LTDA/
│   │   │   │   └── Hyundai_10082023__padrao_1__10394422000142__31122022__37d1409f.xlsx
│   │   │   ├── 10500221000182__LIBRA_LIGAS_DO_BRASIL_S_A/
│   │   │   │   ├── LIBRA LIGAS - 08 04 2024__padrao_1__10500221000182__31122022__2c592270.xlsx
│   │   │   │   └── LIBRAS RATING 09032026__padrao_2__10500221000182__31122024__c30c7fde.xlsx
│   │   │   ├── 10622118000105__FOUNTAIN_S_A/
│   │   │   │   └── Fontain 05032024__padrao_1__10622118000105__31122022__f330b158.xlsx
│   │   │   ├── 10656452000180__VOTORANTIM_CIMENTOS_N_NE_S_A/
│   │   │   │   └── VOTORANTIM NNE 20082025__padrao_1__10656452000180__31122024__51733d10.xlsx
│   │   │   ├── 10858291000107__COMPANHIA_BRASILEIRA_DE_VIDROS_PLANOS_-_CBVP/
│   │   │   │   └── VIVIX 28_07_2022__padrao_1__10858291000107__31122021__2351215a.xlsx
│   │   │   ├── 10914514000106__PB_BRASIL_INDÚSTRIA_E_COMÉRCIO_DE_GELATINAS_LTDA/
│   │   │   │   └── PB Gelatinas_03_10_2022__padrao_1__10914514000106__31122021__4ca0b278.xlsx
│   │   │   ├── 11252642000102__TROMBINI_EMBALAGENS_S.A._E_CONTROLADAS/
│   │   │   │   └── Trombini_10_11_2022__padrao_1__11252642000102__31122021__5f37c16e.xlsx
│   │   │   ├── 11252642000102__TROMBINI_EMBALAGENS_S_A/
│   │   │   │   ├── TROMBINI - 15.07.2024__padrao_1__11252642000102__31122023__68ca077f.xlsx
│   │   │   │   └── TROMBINI 28082023__padrao_1__11252642000102__31122022__8b30b31b.xlsx
│   │   │   ├── 11421994000136__ORIZON_VALORIZACAO_DE_RESIDUOS_S.A/
│   │   │   │   └── ORIZON 25092025__padrao_1__11421994000136__31122024__d945d0e7.xlsx
│   │   │   ├── 11517262000144__EXTRAMIX_-_CONCRETO_LTDA/
│   │   │   │   └── EXTRAMIX - Avaliação Middle__padrao_1__11517262000144__31122021__04d329eb.xlsx
│   │   │   ├── 11517841000197__COMPANHIA_SULAMERICANA_DE_DISTRIBUIÇÃO/
│   │   │   │   └── CIA Sulamericana de Distribuição sem epr__padrao_1__11517841000197__31122022__dd3fbe3b.xlsx
│   │   │   ├── 11778932000186__BRASWELL_PAPEL_E_CELULOSE_LTDA/
│   │   │   │   └── Braswell__padrao_1__11778932000186__31122021__ba08c86c.xlsx
│   │   │   ├── 11907140000164__KRONA_TUBOS_E_CONEXOES_DO_NORDESTE_LTDA/
│   │   │   │   └── KRONA TUBOS e CONEXOES 28042025__padrao_1__11907140000164__31122024__3c5b11ac.xlsx
│   │   │   ├── 12009135000105__ALIANÇA_GERAÇÃO_DE_ENERGIA_S.A/
│   │   │   │   └── ALIANÇA GERAÇÃO 17072025__padrao_1__12009135000105__31122024__7094c94e.xlsx
│   │   │   ├── 12056613000120__MINERACAO_USIMINAS_S.A/
│   │   │   │   └── MINERACAO USMINAS 13082026__padrao_3__12056613000120__31122025__a98f4987.xlsx
│   │   │   ├── 12091809000155__3R_PETROLEUM_OLEO_E_GAS_S.A/
│   │   │   │   └── 3R PETROLEUM  22042024__padrao_1__12091809000155__31122023__29e292f7.xlsx
│   │   │   ├── 12091809000155__BRAVA_ENERGIA_S.A/
│   │   │   │   ├── 3R PETROLEUM 13082025__padrao_1__12091809000155__31122024__7004cc19.xlsx
│   │   │   │   └── BRAVA 15052026__padrao_2__12091809000155__31122025__71c3017b.xlsx
│   │   │   ├── 12094570000177__MINERACAO_PARAGOMINAS_S.A/
│   │   │   │   └── MINERAÇÃO PARAGOMINAS - 07082025__padrao_1__12094570000177__31122024__647fa294.xlsx
│   │   │   ├── 12094570000177__MINERAÇÃO_PARAGOMINAS_S.A/
│   │   │   │   └── PARAGOMINAS 03082026__padrao_3__12094570000177__31122025__9cdebf6c.xlsx
│   │   │   ├── 12125536000112__SAO_EUTIQUIANO_PARTICIPACOES_S.A/
│   │   │   │   └── ficha São Eutiquiano Participações (Grup__padrao_1__12125536000112__31122021__bbcc8781.xlsx
│   │   │   ├── 12147176000150__A100_ROW_SERVICOS_DE_DADOS_BRASIL_LTDA/
│   │   │   │   └── A 100 ROW Serviços de Dados 10082023__padrao_1__12147176000150__31122022__69cb53ad.xlsx
│   │   │   ├── 12884632000144__GV_DO_BRASIL_INDUSTRIA_E_COMERCIO_DE_ACO_LTDA/
│   │   │   │   └── FICHA_CONSUMIDORES_GV_DO_BRASIL_FINAL__padrao_3__12884632000144__31122025__7ad7c88c.xlsx
│   │   │   ├── 12919786000124__TCP_-_TERMINAL_DE_CONTEINERES_DE_PARANAGUA_S_A/
│   │   │   │   ├── TCP 04082025__padrao_1__12919786000124__31122024__e04db3bc.xlsx
│   │   │   │   └── TCP RATING 04112025__padrao_2__12919786000124__04112025__0006d6f3.xlsx
│   │   │   ├── 12919786000124__TCP_–_TERMINAL_DE_CONTÊINERES_DE_PARANAGUÁ_S.A/
│   │   │   │   └── TCP_Paranaguá_16_01_2023__padrao_1__12919786000124__31122021__151f3305.xlsx
│   │   │   ├── 13200257000139__ILROCHA_EMPREENDIMENTOS_E_PARTICIPACOES_S_A/
│   │   │   │   └── Grupo Rocha 23082023__padrao_1__13200257000139__31122022__ae38bc26.xlsx
│   │   │   ├── 13348048000137__CENTRAL_ENERGETICA_PALMEIRAS_S.A/
│   │   │   │   └── CEPASA 08072025__padrao_1__13348048000137__31122024__c9708129.xlsx
│   │   │   ├── 13416922000126__ARAMART_INDUSTRIA_DE_ARAMADOS_LTDA/
│   │   │   │   └── ARAMART 28072026__padrao_3__13416922000126__31122025__f1d7f510.xlsx
│   │   │   ├── 13504675000110__EMPRESA_BAIANA_DE_AGUAS_E_SANEAMENTO_SA/
│   │   │   │   ├── EMBASA 14042025__padrao_1__13504675000110__31122024__f3945173.xlsx
│   │   │   │   └── EMBASA 18062026__padrao_3__13504675000110__31122025__584292c0.xlsx
│   │   │   ├── 13573332000107__KORDSA_BRASIL_S.A/
│   │   │   │   ├── KORDSA_13032025__padrao_1__13573332000107__31122023__f5ca9860.xlsx
│   │   │   │   └── KORDSA_20_04_2022__padrao_1__13573332000107__31122021__fb64e12b.xlsx
│   │   │   ├── 13743550000142__ASCENTY_DATA_CENTERS_E_TELECOMUNICACOES_S_A/
│   │   │   │   ├── ASCENTY 09072025__padrao_1__13743550000142__31122024__d4b664d0.xlsx
│   │   │   │   ├── ASCENTY 21052026__padrao_2__13743550000142__31122025__78981805.xlsx
│   │   │   │   └── ASCENTY RATING 13102023__padrao_2__13743550000142__88a12623.xlsx
│   │   │   ├── 13788120000147__ELEKEIROZ_S.A/
│   │   │   │   └── ELEKEIROZ 19082026__padrao_3__13788120000147__31122025__c86acae8.xlsx
│   │   │   ├── 13788120000147__ELEKEIROZ_S_A/
│   │   │   │   └── ELEKEIROZ_15_08_2024__padrao_1__13788120000147__31122023__619c79c6.xlsx
│   │   │   ├── 13816470000170__SUMITOMO_RUBBER_DO_BRASIL_LTDA/
│   │   │   │   └── Sumitomo_10082023__padrao_1__13816470000170__31122022__5d63d739.xlsx
│   │   │   ├── 14522178000107__AEROPORTOS_BRASIL_-_VIRACOPOS_S.A/
│   │   │   │   └── VIRACOPOS - 04042024__padrao_1__14522178000107__31122023__3cff52a2.xlsx
│   │   │   ├── 14675270000107__EUCATEX_INDUSTRIA_E_COMERCIO_LTDA/
│   │   │   │   └── EUCATEX RATING 28102025__padrao_2__14675270000107__31122024__01b2486d.xlsx
│   │   │   ├── 14807945000124__SANSUY_S_A_INDUSTRIA_DE_PLASTICOS/
│   │   │   │   └── SANSUY 10062025 v2__padrao_1__14807945000124__31122024__d21b295c.xlsx
│   │   │   ├── 15091769000130__CONSORCIO_BOULEVARD_SHOPPING_VILA_VELHA/
│   │   │   │   └── SHOPPING VILHA  VELHA RATING 19032026__padrao_2__15091769000130__31122024__66dbf66d.xlsx
│   │   │   ├── 15141799000103__CIA_DE_FERRO_LIGAS_DA_BAHIA_FERBASA/
│   │   │   │   ├── FERBASA 00355224__padrao_1__15141799000103__31122024__c5b05af3.xlsx
│   │   │   │   ├── FERBASA 28052026__padrao_2__15141799000103__31122025__0fb308d6.xlsx
│   │   │   │   └── ficha FERBASA 2022__padrao_1__15141799000103__31122021__f07a2e54.xlsx
│   │   │   ├── 15170723000106__LIGA_ALVARO_BAHIA_CONTRA_A_MORTALIDADE_INFANTIL/
│   │   │   │   └── LIGA ALVARO BAHIA RATING 03112025__padrao_2__15170723000106__31122024__081ce4f0.xlsx
│   │   │   ├── 15186359000172__ASSOCIACAO_HOSPITALAR_SANTANA/
│   │   │   │   └── Associação Hospitalar Santana - Avaliaçã__padrao_1__15186359000172__31122021__710675af.xlsx
│   │   │   ├── 15375991000164__TODIMO_MATERIAIS_PARA_CONSTRUCAO_SA/
│   │   │   │   └── TODIMO_06122024__padrao_1__15375991000164__31122023__f0c78640.xlsx
│   │   │   ├── 15578569000106__CONCESSIONARIA_DO_AEROPORTO_INTERNACIONAL_DE_GUARULHOS_S.A/
│   │   │   │   └── AEROPORTO DE GUARULHOS 28082025__padrao_1__15578569000106__31122024__7db2b456.xlsx
│   │   │   ├── 16404287000155__SUZANO_S.A/
│   │   │   │   ├── Suzano 01022024 sem eprotocolo__padrao_1__16404287000155__31122023__e4e77d90.xlsx
│   │   │   │   ├── SUZANO 29052026__padrao_2__16404287000155__31122025__6796f705.xlsx
│   │   │   │   ├── SUZANO RATING 03122025__padrao_2__16404287000155__31122024__2d082e4e.xlsx
│   │   │   │   └── SUZANO_2023_07_03__padrao_1__16404287000155__31122022__d3b48d04.xlsx
│   │   │   ├── 16433626000121__INDUSTRIA_VIDREIRA_DO_NORDESTE_LTDA/
│   │   │   │   └── INDUSTRIA VIDREIRA DO NORDESTE RATING 04__padrao_2__16433626000121__12072012__e2280bbb.xlsx
│   │   │   ├── 16617789000164__AGROPEU-AGRO_INDUSTRIAL_DE_POMPEU_S_A/
│   │   │   │   └── AGROPÉU 18062025__padrao_1__16617789000164__31122024__e3b1ff6d.xlsx
│   │   │   ├── 16628281000161__SAMARCO_MINERACAO_S.A/
│   │   │   │   ├── SAMARCO 13102025__padrao_2__16628281000161__ed4b5b08.xlsx
│   │   │   │   ├── SAMARCO 21082026__padrao_3__16628281000161__31122025__76f0a669.xlsx
│   │   │   │   └── SAMARCO RATING 23122025__padrao_2__16628281000161__31122024__9e9328fb.xlsx
│   │   │   ├── 16628281000161__SAMARCO_MINERACAO_S.A._EM_RECUPERACAO_JUDICIAL/
│   │   │   │   └── SAMARCO 16102023__padrao_1__16628281000161__31122022__31ef524c.xlsx
│   │   │   ├── 16701716003686__FCA_FIAT_CHRYSLER_AUTOMOVEIS_BRASIL_LTDA/
│   │   │   │   └── FCA Fiat-Chrysler_22_08_2022__padrao_1__16701716003686__31122021__2a28dad2.xlsx
│   │   │   ├── 16820052000144__PRIMA_FOODS_S.A/
│   │   │   │   └── PRIMA FOODS RATING 27012026__padrao_2__16820052000144__31122024__7b6fb90a.xlsx
│   │   │   ├── 16933590000145__MINASLIGAS_S.A/
│   │   │   │   └── MINASLIGAS 07052026__padrao_2__16933590000145__31122024__8ec8bb49.xlsx
│   │   │   ├── 17170150000146__VALLOUREC_TUBOS_DO_BRASIL_LTDA/
│   │   │   │   └── VALLOUREC TUBOS RATING 08012025__padrao_2__17170150000146__e1278c9e.xlsx
│   │   │   ├── 17210843000115__BRASIL_TROPICAL_HOTEL_E_CLUBE_DE_VIAGENS_LTDA/
│   │   │   │   └── Brasil Tropical 13072023__padrao_1__17210843000115__31122022__3a5721a3.xlsx
│   │   │   ├── 17221771000101__LIGAS_DE_ALUMINIO_SA_LIASA/
│   │   │   │   ├── LIASA 05012024 v2__padrao_1__17221771000101__31122022__fd466e74.xlsx
│   │   │   │   ├── LIASA 18062025__padrao_1__17221771000101__31122024__81507629.xlsx
│   │   │   │   └── LIASA RATING 24102025__padrao_2__17221771000101__31122023__00ddca54.xlsx
│   │   │   ├── 17227422000105__GERDAU_ACOMINAS_S_A/
│   │   │   │   ├── GERDAU ACOMINAS RATING 11122025__padrao_2__17227422000105__31122024__c33ad803.xlsx
│   │   │   │   └── GERDAU Açominas 11122024__padrao_1__17227422000105__31122023__27d74962.xlsx
│   │   │   ├── 17469701000177__ARCELORMITTAL_BRASIL_S.A/
│   │   │   │   ├── ARCELORMITTAL 13052026__padrao_2__17469701000177__31122025__f7f419c2.xlsx
│   │   │   │   └── ARCELORMITTAL RATING 05112025__padrao_2__17469701000177__31122024__c02ec233.xlsx
│   │   │   ├── 18067083000100__NOVA_FIACAO_INDUSTRIA_TEXTIL_S.A/
│   │   │   │   └── NOVA FIAÇAO 14052026__padrao_2__18067083000100__31122025__01f3499f.xlsx
│   │   │   ├── 18269125000187__BIOHOSP_PRODUTOS_HOSPITALARES_LTDA/
│   │   │   │   └── BIOHOSP 15072026__padrao_3__18269125000187__31122025__a871e09a.xlsx
│   │   │   ├── 18279158000108__RIMA_INDUSTRIAL_S_A/
│   │   │   │   ├── RIMA INDSUTRIAL 07072025__padrao_1__18279158000108__31122024__f98d69cd.xlsx
│   │   │   │   └── RIMA INDUSTRIAL RATING 04112025__padrao_2__18279158000108__31122025__dca15e7f.xlsx
│   │   │   ├── 18626084000139__NATURAFRIG_ALIMENTOS_LTDA/
│   │   │   │   └── NATURAFRIG RATING 20022026__padrao_2__18626084000139__31122024__635e86e3.xlsx
│   │   │   ├── 18788137000118__BIOENERGIA_BARRA_LTDA/
│   │   │   │   └── BIOENERGIA BARRA_30062023__padrao_1__18788137000118__31122021__287dcdcd.xlsx
│   │   │   ├── 18803654000461__GTOP_DISTRIBUICAO_LTDA/
│   │   │   │   └── GTOP RATING 12122025__padrao_2__18803654000461__31122024__d93eeb92.xlsx
│   │   │   ├── 18845076000183__TES_-_TERMINAL_EXPORTADOR_DE_SANTOS/
│   │   │   │   ├── LDC TES 10102025 RATING__padrao_2__18845076000183__fd5967b0.xlsx
│   │   │   │   └── LDC TES 30062025__padrao_1__18845076000183__31122024__9caa9b20.xlsx
│   │   │   ├── 18845076000183__TES_-_TERMINAL_EXPORTADOR_DE_SANTOS_S.A/
│   │   │   │   └── TES Terminal Exp Santos 05052026__padrao_2__18845076000183__31122025__832fb961.xlsx
│   │   │   ├── 18891185000137__COMPANHIA_DO_METRO_DA_BAHIA/
│   │   │   │   ├── METRO BAHIA 08102025__padrao_2__18891185000137__ba58f9cb.xlsx
│   │   │   │   └── METRO BAHIA 21082025__padrao_1__18891185000137__31122024__59440162.xlsx
│   │   │   ├── 19166180000104__BRASFRIGO_S_A/
│   │   │   │   └── BRASFRIGO 15062026__padrao_3__19166180000104__31122025__6798207a.xlsx
│   │   │   ├── 19674909000153__CONCESSIONARIA_DO_AEROPORTO_INTERNACIONAL_DE_CONFINS_S_A/
│   │   │   │   └── Aeroporto Confins 25032025__padrao_1__19674909000153__31122024__6664881c.xlsx
│   │   │   ├── 19726111000108__CONCESSIONARIA_AEROPORTO_RIO_DE_JANEIRO_S.A/
│   │   │   │   └── RIO GALEAO RATING 04112025__padrao_2__19726111000108__31122024__8dc9e566.xlsx
│   │   │   ├── 20003699000150__FS_INDUSTRIA_DE_BIOCOMBUSTIVEIS_LTDA/
│   │   │   │   └── FICHA_CONSUMIDORES_FS_BIOENERGIA_CORRIGI__padrao_3__20003699000150__31032026__38e5ddcc.xlsx
│   │   │   ├── 20300157003912__NOVO_ATACADO_COMERCIO_DE_ALIMENTOS_SA/
│   │   │   │   └── NOVO ATACAREJO 28102025__padrao_2__20300157003912__31122024__cb6ebbfa.xlsx
│   │   │   ├── 20346524000146__KINROSS_BRASIL_MINERACAO_S_A/
│   │   │   │   └── KINROSS 28102025__padrao_2__20346524000146__31122025__f9e1ec67.xlsx
│   │   │   ├── 21109697000103__COMPANHIA_DE_CIMENTO_CAMPEAO_ALVORADA_-_CCA/
│   │   │   │   └── COMPANHIA DE CIMENTO CAMPEAO ALVORADA RA__padrao_2__21109697000103__31122024__a9cb11bf.xlsx
│   │   │   ├── 21399573000100__SUBCONDOMINIO_SHOPPING_CENTER_RIOMAR_FORTALEZA/
│   │   │   │   └── Cessão Flexoprint para All4Labels__padrao_1__21399573000100__31122021__d16e4967.xlsx
│   │   │   ├── 21812954000179__EDF_EN_DO_BRASIL_PARTICIPACOES_LTDA/
│   │   │   │   └── EDF 24072025 v2__padrao_1__21812954000179__31122024__94afbcc1.xlsx
│   │   │   ├── 21819182000105__DIP_FRANGOS_S.A/
│   │   │   │   ├── DIP FRANGOS - 21072025__padrao_1__21819182000105__31122024__7d4d3396.xlsx
│   │   │   │   └── DIP FRANGOS 28042026__padrao_2__21819182000105__31122025__81e7aa73.xlsx
│   │   │   ├── 23096269000119__RIO_PARANA_ENERGIA_S.A/
│   │   │   │   └── RIO PARANÁ ENERGIA 26112024__padrao_1__23096269000119__31122023__b5079bd6.xlsx
│   │   │   ├── 23637697000101__ALCOA_ALUMINIO_S_A/
│   │   │   │   ├── ALCOA 08042026__padrao_2__23637697000101__31122025__c962acb8.xlsx
│   │   │   │   └── ALCOA ALUMINIO 30052025__padrao_1__23637697000101__31122024__bed80a90.xlsx
│   │   │   ├── 23798846000114__HOSPITAL_DE_NOSSA_SENHORA_DAS_DORES/
│   │   │   │   └── HOSPITAL_NOSSA_SENHORA_DAS_DORES_2103202__padrao_1__23798846000114__31122021__38c5670b.xlsx
│   │   │   ├── 24168115000158__ARDAGH_METAL_PACKAGING_BRASIL_LTDA/
│   │   │   │   └── Ardagh Metal 26_09_2022__padrao_1__24168115000158__31122021__71a4659b.xlsx
│   │   │   ├── 24396489000120__BRK_AMBIENTAL_PARTICIPACOES_S.A/
│   │   │   │   └── BRK Ambiental - Avaliação Middle__padrao_1__24396489000120__31122021__211c4cd3.xlsx
│   │   │   ├── 24550050000100__JARDIM_BOTÂNICO_GERAÇÃO_DE_ENERGIA_E_PARTICIPAÇÕES_S.A/
│   │   │   │   └── Jardim Botânico Participações 28-10-2025__padrao_2__24550050000100__31122024__b2180e91.xlsx
│   │   │   ├── 24990777000109__GRUPO_MATEUS_S.A/
│   │   │   │   └── GRUPO MATHEUS RATING 10032026__padrao_2__24990777000109__31122024__ffa5400f.xlsx
│   │   │   ├── 25201024000130__RAIZEN-GEO_BIOGAS_S.A/
│   │   │   │   └── Raízen Geo Biogás 13022025__padrao_1__25201024000130__31122024__48909b50.xlsx
│   │   │   ├── 26051817000182__POLO_FILMS_INDUSTRIA_E_COMERCIO_S_A/
│   │   │   │   └── POLO FILMS 20-07-2022__padrao_1__26051817000182__31122021__d5e79d2c.xlsx
│   │   │   ├── 27352303000120__UHE_SÃO_SIMÃO_ENERGIA_S.A/
│   │   │   │   └── UHE SAO SIMAO 28082025__padrao_1__27352303000120__31122024__9efd37d4.xlsx
│   │   │   ├── 27515154002035__PROQUIGEL_QUIMICA_S_A/
│   │   │   │   └── UNIGEL - Proquigel 30-01-2023__padrao_1__27515154002035__31122021__671e6046.xlsx
│   │   │   ├── 28127926000242__ASSOCIACAO_EVANGELICA_BENEFICENTE_ESPIRITO-SANTENSE_-_AEBES/
│   │   │   │   └── AEBES HEJSN 01122023__padrao_1__28127926000242__31122022__ce751321.xlsx
│   │   │   ├── 28127926000242__ASSOCIAÇÃO_EVANGÉLICA_BENEFICENTE_ESPÍRITO_SANTENSE_-_AEBES/
│   │   │   │   └── HEJSN_19_10_2022__padrao_1__28127926000242__31122021__52185f15.xlsx
│   │   │   ├── 28547761000187__PARK_SHOPPING_BOULEVARD_LINHA_VERDE_LTDA/
│   │   │   │   └── SHOPPING BOULEVARD RATING 16032026__padrao_2__28547761000187__31122024__d7120e4b.xlsx
│   │   │   ├── 28969492000147__PARANA_BOI_COMERCIO_DE_CARNES_LTDA/
│   │   │   │   └── PARANA BOI 24042026__padrao_2__28969492000147__31122025__cae89133.xlsx
│   │   │   ├── 29067113000196__POLIMIX_CONCRETO_LTDA/
│   │   │   │   └── POLIMIX_06062023__padrao_1__29067113000196__31122021__9b15ff1d.xlsx
│   │   │   ├── 29316596000115__INPASA_AGROINDUSTRIAL_S_A/
│   │   │   │   └── INPASA RATING 10122025__padrao_2__29316596000115__31122024__a709f844.xlsx
│   │   │   ├── 29667227000177__ARLANXEO_BRASIL_S.A/
│   │   │   │   └── ARLANXEO_21032023__padrao_1__29667227000177__31122021__a5dbc7c4.xlsx
│   │   │   ├── 29938085000135__CONCESSIONARIA_DAS_LINHAS_5_E_17_DO_METRO_DE_SAO_PAULO_S.A/
│   │   │   │   └── LINHAS 5 E 17 06072026__padrao_3__29938085000135__31122025__5c426bda.xlsx
│   │   │   ├── 31590862000145__COPAPA_CIA_PADUANA_DE_PAPEIS/
│   │   │   │   └── COPAPA RATING 17112025__padrao_2__31590862000145__31122024__59db035a.xlsx
│   │   │   ├── 32112142000137__FOSNOR_-_FOSFATADOS_DO_NORTE-NORDESTE_S_A/
│   │   │   │   └── FOSNOR 20-02-225__padrao_1__32112142000137__31122023__5f83b303.xlsx
│   │   │   ├── 32140332000168__RVTRANS_TRANSPORTE_URBANO_S.A/
│   │   │   │   └── RVTRANS 31072026__padrao_3__32140332000168__31122025__6a95dac7.xlsx
│   │   │   ├── 32184195000163__VALGROUP_BRASIL_PARTICIPACOES_LTDA/
│   │   │   │   └── VALGROUP PACKAGING SOLUTIONS - Avaliação__padrao_1__32184195000163__31122021__ca9dc25e.xlsx
│   │   │   ├── 33000167000101__PETROLEO_BRASILEIRO_S_A_PETROBRAS/
│   │   │   │   ├── PETROBRAS 10062026__padrao_3__33000167000101__31122025__cff13f1b.xlsx
│   │   │   │   └── PETROBRAS RATING 10112025__padrao_2__33000167000101__31122024__1fe799d0.xlsx
│   │   │   ├── 33009911000139__SOUZA_CRUZ_LTDA/
│   │   │   │   └── SOUZA CRUZ RATING 04032026__padrao_2__33009911000139__31122024__ab558a28.xlsx
│   │   │   ├── 33010786000187__CITROSUCO_S_A_AGROINDUSTRIA/
│   │   │   │   └── CITROSUCO_10042025__padrao_1__33010786000187__31122024__f5c8c50c.xlsx
│   │   │   ├── 33042730000104__COMPANHIA_SIDERURGICA_NACIONAL/
│   │   │   │   ├── CSN 04062025__padrao_1__33042730000104__31122024__7c20df72.xlsx
│   │   │   │   ├── CSN 19062026__padrao_3__33042730000104__31122025__5ecc93e4.xlsx
│   │   │   │   └── CSN 31-07-224__padrao_1__33042730000104__31122023__b329253d.xlsx
│   │   │   ├── 33200056000149__LOJAS_RIACHUELO_S_A/
│   │   │   │   ├── ficha modelo livres acima de 2MWm__padrao_1__33200056000149__31122022__7afaa4a4.xlsx
│   │   │   │   └── RIACHUELO_05072023__padrao_1__33200056000149__31122021__878b1ccc.xlsx
│   │   │   ├── 33352394000104__COMPANHIA_ESTADUAL_DE_AGUAS_E_ESGOTOS_CEDAE/
│   │   │   │   └── CEDAE_23082023__padrao_1__33352394000104__31122022__d872e0c3.xlsx
│   │   │   ├── 33390170000189__APERAM_INOX_AMERICA_DO_SUL_S.A/
│   │   │   │   └── APERAM RATING 18032026__padrao_2__33390170000189__31122024__acaef2e6.xlsx
│   │   │   ├── 33443024000174__CONSORCIO_TRANSVIDA/
│   │   │   │   └── TRANSVIDA RATING 20022026__padrao_2__33443024000174__31122024__ebf06f26.xlsx
│   │   │   ├── 33592510000154__VALE_S.A/
│   │   │   │   ├── FICHA CONSUMIDORES V1 (2)_VALE_PREENCHID__padrao_3__33592510000154__31122025__96ea0158.xlsx
│   │   │   │   └── VALE 30-05-2025__padrao_1__33592510000154__31122024__d96b8c37.xlsx
│   │   │   ├── 33611500000119__GERDAU_S.A/
│   │   │   │   ├── GERDAU MATRIZ 20052026__padrao_2__33611500000119__31122025__d7894696.xlsx
│   │   │   │   ├── GERDAU SA - 13062025__padrao_1__33611500000119__31122024__ff49d357.xlsx
│   │   │   │   ├── GERDAU SA 11122024__padrao_1__33611500000119__31122023__ba5db8b0.xlsx
│   │   │   │   └── GERDAU_23062023__padrao_1__33611500000119__31122022__826f2f98.xlsx
│   │   │   ├── 33641663000144__FUNDACAO_GETULIO_VARGAS/
│   │   │   │   └── FGV 15102025__padrao_2__33641663000144__c39b622a.xlsx
│   │   │   ├── 33919741000120__AEROPORTOS_DO_NORDESTE_DO_BRASIL_S.A/
│   │   │   │   └── AEROPORTOS DO NORDESTE_16032023__padrao_1__33919741000120__31122021__3e497721.xlsx
│   │   │   ├── 33931478000194__SALOBO_METAIS_S.A/
│   │   │   │   └── SALOBO METAIS 20082026__padrao_3__33931478000194__31122025__6d837be4.xlsx
│   │   │   ├── 33931478000194__SALOBO_METAIS_S_A/
│   │   │   │   └── SALOBO METAIS 28072025__padrao_1__33931478000194__31122024__706c5c71.xlsx
│   │   │   ├── 33958695000178__UNIPAR_CARBOCLORO_S.A/
│   │   │   │   ├── UNIPAR 19052026__padrao_2__33958695000178__31122025__42d746df.xlsx
│   │   │   │   └── UNIPAR RATING 04112025__padrao_2__33958695000178__31122024__2a408a23.xlsx
│   │   │   ├── 34562112000158__SCALA_DATA_CENTERS_S.A/
│   │   │   │   ├── SCALA DATA CENTERS 0508226__padrao_3__34562112000158__31122025__1d63ec4b.xlsx
│   │   │   │   └── SCALA DATA CENTERS 2025__padrao_1__34562112000158__31122024__2ae4249c.xlsx
│   │   │   ├── 34954956000144__A)_DADOS_DE_DEMONSTRAÇÕES_FINANCEIRAS_EM_R$_MIL/
│   │   │   │   └── GWEST RATING 03022026__padrao_2__34954956000144__31122024__eeb136a9.xlsx
│   │   │   ├── 35402759000185__BIMBO_DO_BRASIL_LTDA/
│   │   │   │   └── Bimbo_02_09_2024__padrao_1__35402759000185__31122023__231c7f61.xlsx
│   │   │   ├── 35820448000136__WHITE_MARTINS_GASES_INDUSTRIAIS_LTDA/
│   │   │   │   ├── WHITE MARTINS 20082025__padrao_1__35820448000136__31122024__ad62bb6e.xlsx
│   │   │   │   └── WHITE MARTINS 30072026__padrao_3__35820448000136__31122025__a26b186f.xlsx
│   │   │   ├── 35984409000174__EDF_RENEWABLES_VERDECOM_COMERCIALIZADORA_LTDA/
│   │   │   │   └── EDF VERDECOM RATING 17102025__padrao_2__35984409000174__31122024__de332121.xlsx
│   │   │   ├── 37589182000198__18.224.058_0001-84/
│   │   │   │   └── Grupo Vertical 30082023__padrao_1__37589182000198__31122022__00057821.xlsx
│   │   │   ├── 38246958000130__UNIGEL_COMERCIALIZADORA_DE_ENERGIA_S.A/
│   │   │   │   └── UNIGEL 24072025__padrao_1__38246958000130__31122024__50daf92c.xlsx
│   │   │   ├── 39449320000169__SUBCONDOMINIO_SHOPPING_CENTER_RIOMAR_FORTALEZA/
│   │   │   │   └── PURO PELLET - Avaliação Middle__padrao_1__39449320000169__31122021__79367da9.xlsx
│   │   │   ├── 39881421000104__COMPANHIA_ESTADUAL_DE_GERAÇÃO_DE_ENERGIA_ELÉTRICA_-_CEEE-G/
│   │   │   │   ├── CEEE RATING 02122025__padrao_2__39881421000104__31122024__6bfe593b.xlsx
│   │   │   │   └── CEEE-G_02_06_2025__padrao_1__39881421000104__31122025__648c1e0d.xlsx
│   │   │   ├── 39913479000192__ASSOCIACAO_DO_HOSPITAL_JARAGUA/
│   │   │   │   ├── Associação do Hospital de Jaragiuá - Ava__padrao_1__39913479000192__31122021__5add7876.xlsx
│   │   │   │   └── Hospital Jaraguá 25072023__padrao_1__39913479000192__31122022__081ce2bd.xlsx
│   │   │   ├── 40172765000123__CNEP_-_CADASTRO_NACIONAL_DE_EMPRESAS_PUNIDAS/
│   │   │   │   └── Cooper Barras 29_09_2022__padrao_1__40172765000123__31122021__18c3925a.xlsx
│   │   │   ├── 40254927000172__PARANA_XISTO_S.A/
│   │   │   │   ├── Paraná Xisto 13012025__padrao_1__40254927000172__31122023__8a645996.xlsx
│   │   │   │   └── Paraná Xisto 22082023__padrao_1__40254927000172__31122022__f5474836.xlsx
│   │   │   ├── 40263170000183__SOLVI_ESSENCIS_AMBIENTAL_S.A/
│   │   │   │   └── SOLVI ESSENCIS RATING 23032026__padrao_2__40263170000183__31122024__0eb99c86.xlsx
│   │   │   ├── 40772936000155__EXTRUSAICK_POLIMEROS_LTDA/
│   │   │   │   └── EXTRUSAICK 17062026__padrao_3__40772936000155__31122025__53315ac2.xlsx
│   │   │   ├── 40797554000186__AMELPLAST_INDUSTRIA_E_COMERCIO_DE_PRODUTOS_PLASTICOS_LTDA/
│   │   │   │   └── AMELPLAST RATING 29012026__padrao_2__40797554000186__31122024__5e23a5af.xlsx
│   │   │   ├── 41052420000107__SOLAR_BEBIDAS_S.A/
│   │   │   │   └── SOLAR BEBIDAS SA RATING 09012026__padrao_2__41052420000107__31122024__d0a958ae.xlsx
│   │   │   ├── 41501877000143__SOLAR.BR_ENERGIA_LTDA/
│   │   │   │   ├── SOLAR BR 25052026__padrao_2__41501877000143__31122025__a891ce48.xlsx
│   │   │   │   ├── SOLAR BR ENERGIA RATING 09012026__padrao_2__41501877000143__31122024__d39a75ce.xlsx
│   │   │   │   └── SOLAR ENERGIAS RATING 12122025__padrao_2__41501877000143__3ca8ece2.xlsx
│   │   │   ├── 41777706000141__REFINARIA_DE_MATARIPE_S.A/
│   │   │   │   └── REFINARIA MATARIPE 17082026__padrao_3__41777706000141__31122025__d6e0cfba.xlsx
│   │   │   ├── 42105890000146__SOUTH32_MINERALS_S.A/
│   │   │   │   └── SOUTH32 18082026__padrao_3__42105890000146__30062025__571c356d.xlsx
│   │   │   ├── 42150391000170__BRASKEM_S.A/
│   │   │   │   ├── BRASKEM - 05 04 2024__padrao_1__42150391000170__31122023__d2f5377c.xlsx
│   │   │   │   ├── BRASKEM 21052026__padrao_2__42150391000170__31122025__920e1508.xlsx
│   │   │   │   ├── BRASKEM 22072025__padrao_1__42150391000170__31122024__d30e969b.xlsx
│   │   │   │   └── Brasken 01022024 sem eprotocolo__padrao_1__42150391000170__31122022__e46bb666.xlsx
│   │   │   ├── 42184226000130__ANGLO_AMERICAN_NIQUEL_BRASIL_LTDA/
│   │   │   │   └── ANGLO AMERICAN 03072026__padrao_3__42184226000130__31122025__105986a0.xlsx
│   │   │   ├── 42184226001969__ANGLO_AMERICAN_NIQUEL_BRASIL_LTDA/
│   │   │   │   ├── Anglo Amercia 27022024 v2__padrao_1__42184226001969__31122022__7480ff57.xlsx
│   │   │   │   └── ANGLO AMERICAN 31.12.2023__padrao_1__42184226001969__31122023__24a19249.xlsx
│   │   │   ├── 42288184000187__-474911/
│   │   │   │   └── LINHAS 8 E 9 07072026__padrao_3__42288184000187__31122025__75010051.xlsx
│   │   │   ├── 42288184000187__A)_ÍNDICE_DE_SOLVÊNCIA_GERAL/
│   │   │   │   └── TRENS DE SP 21082025__padrao_1__42288184000187__31122024__dce7cff5.xlsx
│   │   │   ├── 42416651000107__NEXA_RECURSOS_MINERAIS_S.A/
│   │   │   │   ├── NEXA 05012026__padrao_2__42416651000107__86b105d8.xlsx
│   │   │   │   ├── NEXA 08072025__padrao_1__42416651000107__31122024__d9ec81d8.xlsx
│   │   │   │   └── NEXA RECURSOS MINERAIS 18062026__padrao_3__42416651000107__31122025__3c5f365b.xlsx
│   │   │   ├── 42422048000138__MINERACAO_AURIZONA_S_A/
│   │   │   │   └── MINERAÇÃO AURIZONA 23082023__padrao_1__42422048000138__31122022__fc7f1b71.xlsx
│   │   │   ├── 42422048000219__MINERACAO_AURIZONA_S_A/
│   │   │   │   └── Mineração Aurizona 17052024__padrao_1__42422048000219__31122022__2e989806.xlsx
│   │   │   ├── 42463174000130__JACOBINA_MINERACAO_E_COMERCIO_LTDA/
│   │   │   │   └── Jacobina Mineração_24_02_2023__padrao_1__42463174000130__31122021__327ee7b7.xlsx
│   │   │   ├── 42566752000164__VILLARES_METALS_S.A/
│   │   │   │   └── VILLARES_14032023__padrao_1__42566752000164__31122021__941054e8.xlsx
│   │   │   ├── 42566752000164__VILLARES_METALS_SA/
│   │   │   │   ├── VILLARES METALS 02072026__padrao_3__42566752000164__31032026__a77923b4.xlsx
│   │   │   │   └── VILLARES METALS RATING 12112025__padrao_2__42566752000164__31032025__5d160aae.xlsx
│   │   │   ├── 42644220000106__AGUAS_DO_RIO_4_SPE_S.A/
│   │   │   │   ├── AEGEA 17072025__padrao_1__42644220000106__31122024__c7c029c3.xlsx
│   │   │   │   ├── AEGEA_RIO4_16122024__padrao_1__42644220000106__31122023__2c3abd4b.xlsx
│   │   │   │   └── AGUAS DO RIO 4__padrao_3__42644220000106__31122025__d499c24e.xlsx
│   │   │   ├── 42956441000101__SOLUCOES_EM_ACO_USIMINAS_S.A/
│   │   │   │   └── USIMINAS 15042026__padrao_2__42956441000101__31122024__fce349a8.xlsx
│   │   │   ├── 43446434000122__CANDEIAS_ESPORTE_LAZER_E_RECREACAO/
│   │   │   │   └── CANDEIAS 15102025__padrao_2__43446434000122__c44589cb.xlsx
│   │   │   ├── 43461789000190__QUIMICA_AMPARO_LTDA/
│   │   │   │   └── Quimica Amparo YPE - Avaliação Middle__padrao_1__43461789000190__31122021__33482fb2.xlsx
│   │   │   ├── 43468701000162__FERNANDEZ_SOCIEDADE_ANONIMA_INDUSTRIA_DE_PAPEL/
│   │   │   │   └── FERNANDEZ INDUSTRIA DE PAPEL RATING 0903__padrao_2__43468701000162__31122024__1425d01b.xlsx
│   │   │   ├── 43545284000104__ALCOESTE_BIOENERGIA_FERNANDOPOLIS_S.A/
│   │   │   │   ├── ALCOESTE BIOENERTIA 04-05-2026__padrao_2__43545284000104__31122024__308b90b9.xlsx
│   │   │   │   └── ALCOESTE FERNANDÓPOLIS 22052026__padrao_2__43545284000104__31122025__08570b90.xlsx
│   │   │   ├── 43619832001760__BRANCO_PERES_AGRO_S_A/
│   │   │   │   └── BRANCO PERES 04052026__padrao_2__43619832001760__31122024__17cffb1e.xlsx
│   │   │   ├── 43776517000180__RESERVA_DE_LUCROS/
│   │   │   │   ├── SABESP 23062026__padrao_3__43776517000180__31122025__252938eb.xlsx
│   │   │   │   └── SABESP RATING 10112025__padrao_2__43776517000180__31122024__f8b32a3b.xlsx
│   │   │   ├── 44145845000140__MELHORAMENTOS_CMPC_LTDA/
│   │   │   │   └── SOFTYS_09_03_2022__padrao_1__44145845000140__31122020__32aa8a21.xlsx
│   │   │   ├── 44145845000140__SOFTYS_BRASIL_LTDA/
│   │   │   │   └── SOFTYS BRASIL 25062025__padrao_1__44145845000140__31122024__ef29230d.xlsx
│   │   │   ├── 45399961000159__UNIMED_DE_SOROCABA_COOPERATIVA_DE_TRABALHO_MEDICO/
│   │   │   │   └── FICHA_CONSUMIDORES_UNIMED_SOROCABA_PREEN__padrao_3__45399961000159__31122025__8f3f21dd.xlsx
│   │   │   ├── 47067525000108__LOUIS_DREYFUS_COMPANY_BRASIL_S.A/
│   │   │   │   ├── LDC 09102025 RATING__padrao_2__47067525000108__7a3537c9.xlsx
│   │   │   │   ├── LDC BRASIL 30062025__padrao_1__47067525000108__31122024__8859b20a.xlsx
│   │   │   │   └── LDC MATRIZ__padrao_2__47067525000108__31122025__f5a61bac.xlsx
│   │   │   ├── 47080619000117__TEREOS_ACUCAR_E_ENERGIA_BRASIL_S.A/
│   │   │   │   └── TEREOS AÇÚCAR RATING 25032026__padrao_2__47080619000117__31032025__645c3bb7.xlsx
│   │   │   ├── 47080619000117__TEREOS_AÇÚCAR_E_ENERGIA_BRASIL_S.A/
│   │   │   │   └── TEREOS ACUCAR 14072026__padrao_3__47080619000117__31032026__f90c07c5.xlsx
│   │   │   ├── 47508411000156__COMPANHIA_BRASILEIRA_DE_DISTRIBUICAO/
│   │   │   │   └── Grupo Pão de Açucar 19032024__padrao_1__47508411000156__31122023__3bc33db2.xlsx
│   │   │   ├── 47508411000156__GRUPO_PAO_DE_AÇUCAR/
│   │   │   │   └── GPA RATING 07112025__padrao_2__47508411000156__31122024__346a9c32.xlsx
│   │   │   ├── 47595863000112__DELTA_INDUSTRIA_CERAMICA_LTDA/
│   │   │   │   └── Delta Indústria Cerâmica 28022025__padrao_1__47595863000112__31122024__4cec4188.xlsx
│   │   │   ├── 47658073000139__ARAUCO_CELULOSE_DO_BRASIL_S.A/
│   │   │   │   └── ARAUCO - 27032025__padrao_1__47658073000139__31122024__afbadae0.xlsx
│   │   │   ├── 47902283000120__SONORA_ESTANCIA_S_A/
│   │   │   │   └── SONORA ESTANCIA 25052026__padrao_2__47902283000120__31032025__cff9298d.xlsx
│   │   │   ├── 47964911000100__USINA_DE_LATICINIOS_JUSSARA_S_A/
│   │   │   │   └── USINA LATICIÍNIOS JUSSARA 08052026__padrao_2__47964911000100__31122025__6c69c7c8.xlsx
│   │   │   ├── 48256824000153__MINERACAO_ONCA_PUMA_S.A/
│   │   │   │   ├── MINERACAO ONCA PUMA 17082026__padrao_3__48256824000153__31122025__f1d0395b.xlsx
│   │   │   │   └── MINERACAO ONCA PUMA RATING 03112025__padrao_2__48256824000153__31122024__49a9edb7.xlsx
│   │   │   ├── 48539407000118__BASF_S.A/
│   │   │   │   └── BASF 14072026__padrao_3__48539407000118__31122025__9e857d60.xlsx
│   │   │   ├── 48539407000118__BASF_SA/
│   │   │   │   ├── BASF 25082025__padrao_1__48539407000118__31122024__3b04d6c2.xlsx
│   │   │   │   └── BASF RATING 14102025__padrao_2__48539407000118__1c474f3e.xlsx
│   │   │   ├── 48539407007392__BASF_SA/
│   │   │   │   └── ficha BASF 2022__padrao_1__48539407007392__31122021__2be29b10.xlsx
│   │   │   ├── 48540421000131__SERVENG_CIVILSAN_S.A._-_EMPRESAS_ASSOCIADAS_DE_ENGENHARIA/
│   │   │   │   └── SERVENG CIVILSAN 18082026__padrao_3__48540421000131__31122025__90ee3480.xlsx
│   │   │   ├── 48540421000131__SERVENG_CIVILSAN_S_A_EMPRESAS_ASSOCIADAS_DE_ENGENHARIA/
│   │   │   │   └── SERVENG CIVILSAN RATING 12112025__padrao_2__48540421000131__31122024__d00caae3.xlsx
│   │   │   ├── 48845556000105__VIDROPORTO_-_UNIDADE_SUDESTE/
│   │   │   │   └── VIDROPORTO RATING 03022026__padrao_2__48845556000105__31122025__be2945fc.xlsx
│   │   │   ├── 48992518000185__DANGLASS_DO_BRASIL_LTDA/
│   │   │   │   └── DANGLASS 29062026__padrao_3__48992518000185__31122025__a25a0b1b.xlsx
│   │   │   ├── 50615144000120__VISTA_FOODS_LTDA/
│   │   │   │   └── Vista Foods 15122023__padrao_1__50615144000120__b96e1a12.xlsx
│   │   │   ├── 50955707000120__HEINZ_BRASIL_S.A/
│   │   │   │   └── Heinz Brasil - Avaliação Middle__padrao_1__50955707000120__31122021__e4804c2d.xlsx
│   │   │   ├── 50955707001100__HEINZ_BRASIL_S.A/
│   │   │   │   └── HEINZ_20032023__padrao_1__50955707001100__31122021__a73afcbb.xlsx
│   │   │   ├── 51466860000156__SAO_MARTINHO_S_A/
│   │   │   │   ├── SAO MARTINHO 01062026__padrao_2__51466860000156__31032026__115501fa.xlsx
│   │   │   │   └── SAO MARTINHO RATING 02022026__padrao_2__51466860000156__31032025__81e28dcb.xlsx
│   │   │   ├── 51784262000125__PEROXIDOS_DO_BRASIL_LTDA/
│   │   │   │   ├── PEROXIDOS 28-04-2026__padrao_2__51784262000125__31122025__f4385d57.xlsx
│   │   │   │   └── Peróxidos_24_02_2023__padrao_1__51784262000125__31122021__95ef0097.xlsx
│   │   │   ├── 52645009000153__FRIGOESTRELA_S_A/
│   │   │   │   ├── Frigoestrela_02052023__padrao_1__52645009000153__31122022__73fa1a2d.xlsx
│   │   │   │   └── FRIGOESTRELA_20_08_2024__padrao_1__52645009000153__31122023__3f9a298b.xlsx
│   │   │   ├── 52736949000158__SYLVAMO_DO_BRASIL_LTDA/
│   │   │   │   └── SYLVAMO_20_07_2022__padrao_1__52736949000158__31122021__ab119e6e.xlsx
│   │   │   ├── 53162783000176__BIORIGIN_S.A/
│   │   │   │   └── BIORIGIN 15072026__padrao_3__53162783000176__31122025__233627cf.xlsx
│   │   │   ├── 53943098000187__BRACELL_SP_CELULOSE_LTDA/
│   │   │   │   └── BRACELL CELULOSE 04082025__padrao_1__53943098000187__31122024__c4d2dd4f.xlsx
│   │   │   ├── 54105671000146__CP_KELCO_BRASIL_S_A/
│   │   │   │   └── CP KELKO RATING 02022026__padrao_2__54105671000146__31122025__d2d47311.xlsx
│   │   │   ├── 54625819000173__EATON_LTDA/
│   │   │   │   └── EATON_23_02_2022__padrao_1__54625819000173__31122021__49d808a2.xlsx
│   │   │   ├── 54672449000125__HOSPITAL_SAO_FRANCISCO_SOCIEDADE_LTDA/
│   │   │   │   └── Hospital São Francisco18_01_23__padrao_1__54672449000125__31122021__e49cdaef.xlsx
│   │   │   ├── 55924836000174__LNSC_PARTICIPACOES_LTDA/
│   │   │   │   └── LSNC RATING 12122025__padrao_2__55924836000174__31122024__94615dd1.xlsx
│   │   │   ├── 56384183000140__IRMANDADE_DA_SANTA_CASA_DE_MISERICORDIA_DE_RIO_CLARO/
│   │   │   │   └── Sta Casa Rio Claro 17102023__padrao_1__56384183000140__31122022__d60f205e.xlsx
│   │   │   ├── 56720428001488__ROMI_S.A/
│   │   │   │   └── ROMI 16052025__padrao_1__56720428001488__31122024__e55c2b1c.xlsx
│   │   │   ├── 57107609000343__RUY_R_DA_ROCHA_PRODUTOS_CERAMICOS_LTDA/
│   │   │   │   └── RUY ROCHA 30042026__padrao_2__57107609000343__31122024__e08d5886.xlsx
│   │   │   ├── 57497539000115__BRIDGESTONE_DO_BRASIL_INDUSTRIA_E_COMERCIO_LTDA/
│   │   │   │   └── Bridgestone do Brasil__padrao_1__57497539000115__31122021__e6b92ba9.xlsx
│   │   │   ├── 57497539000700__BRIDGESTONE_DO_BRASIL_INDUSTRIA_E_COMERCIO_LTDA/
│   │   │   │   └── Bridgestone_24_08_2022 - 2__padrao_1__57497539000700__31122021__67726dd5.xlsx
│   │   │   ├── 57497539001359__BRIDGESTONE_DO_BRASIL_INDUSTRIA_E_COMERCIO_LTDA/
│   │   │   │   └── Bridgestone_24_08_2022 - 4__padrao_1__57497539001359__31122021__4a810282.xlsx
│   │   │   ├── 57497539001600__BRIDGESTONE_DO_BRASIL_INDUSTRIA_E_COMERCIO_LTDA/
│   │   │   │   └── Bridgestone_24_08_2022 - 3__padrao_1__57497539001600__31122021__72e46536.xlsx
│   │   │   ├── 57507378000365__EMS_SA/
│   │   │   │   └── Grupo NC - Avaliação Middle__padrao_1__57507378000365__31122021__9216b56b.xlsx
│   │   │   ├── 57507626000106__RHODIA_BRASIL_S.A/
│   │   │   │   └── RHODIA BRASIL 20072026__padrao_3__57507626000106__31122025__42f2e240.xlsx
│   │   │   ├── 59104422000150__VOLKSWAGEN_DO_BRASIL_INDUSTRIA_DE_VEICULOS_AUTOMOTORES_LTDA/
│   │   │   │   ├── Volks 21-07-2022__padrao_1__59104422000150__31122021__2ab56d9e.xlsx
│   │   │   │   └── VW do Brasil_18072023__padrao_1__59104422000150__31122022__15a9ef87.xlsx
│   │   │   ├── 59105999000186__WHIRLPOOL_S.A/
│   │   │   │   └── WHIRLPOOL_24_04_2023__padrao_1__59105999000186__31122021__8e290f27.xlsx
│   │   │   ├── 59106666000171__TERMOMECANICA_SAO_PAULO_S_A/
│   │   │   │   └── Termomecânica São Paulo_05102023__padrao_1__59106666000171__31122022__870f2511.xlsx
│   │   │   ├── 59221316000156__PLASTICOS_AMSTERDAN_LTDA/
│   │   │   │   └── PLASTICOS AMSTERDAN 13072026__padrao_3__59221316000156__31122025__8f8fd868.xlsx
│   │   │   ├── 59275792000150__GENERAL_MOTORS_DO_BRASIL_LTDA/
│   │   │   │   └── GM do Brasil - Avaliação Middle__padrao_1__59275792000150__31122022__1db2ba16.xlsx
│   │   │   ├── 59970947000178__CASA_DE_SAUDE_SANTA_HELENA_LTDA/
│   │   │   │   └── SANTAHELENA_2023_03_15__padrao_1__59970947000178__31122021__a5ffc848.xlsx
│   │   │   ├── 60476884000187__MAHLE_METAL_LEVE_S.A/
│   │   │   │   ├── MAHLE 13082026__padrao_3__60476884000187__31122025__69d35748.xlsx
│   │   │   │   └── METAL LEVE - 21082025__padrao_1__60476884000187__31122024__4e81cb8e.xlsx
│   │   │   ├── 60498706000157__CARGILL_AGRICOLA_S_A/
│   │   │   │   ├── CARGILL 11062026 - REVISÃO__padrao_3__60498706000157__31122025__5a32ff1f.xlsx
│   │   │   │   ├── CARGILL 15072025__padrao_1__60498706000157__31122024__006dd374.xlsx
│   │   │   │   └── CARGILL RATING 13102025__padrao_2__60498706000157__b0d7ca82.xlsx
│   │   │   ├── 60500246000154__GOODYEAR_DO_BRASIL_PRODUTOS_DE_BORRACHA_LTDA/
│   │   │   │   └── Goodyear 2022-07-12__padrao_1__60500246000154__31122021__0c561fbb.xlsx
│   │   │   ├── 60561800000103__NOVELIS_DO_BRASIL_LTDA/
│   │   │   │   ├── NOVELIS 05062026__padrao_2__60561800000103__31032026__0afb3deb.xlsx
│   │   │   │   └── NOVELIS 08052026__padrao_2__60561800000103__31032025__7328f258.xlsx
│   │   │   ├── 60619202000148__MESSER_GASES_LTDA/
│   │   │   │   ├── MESSER GASES 02072025__padrao_1__60619202000148__31122024__4a1a3122.xlsx
│   │   │   │   ├── Messer Gases 16112023__padrao_1__60619202000148__31122022__24a9ae63.xlsx
│   │   │   │   ├── MESSER GASES 22072026__padrao_3__60619202000148__31122025__171dc857.xlsx
│   │   │   │   └── MESSER_27_12_2022__padrao_1__60619202000148__31122021__d587eeb1.xlsx
│   │   │   ├── 60619202003325__MESSER_GASES_LTDA/
│   │   │   │   └── MESSER GASES_05052022__padrao_1__60619202003325__31122021__9fe720c6.xlsx
│   │   │   ├── 60665981000118__UNIAO_QUIMICA_FARMACEUTICA_NACIONAL_S_A/
│   │   │   │   └── União Química 14112023__padrao_1__60665981000118__31122022__b0bfc58c.xlsx
│   │   │   ├── 60746948000112__BANCO_BRADESCO_S.A/
│   │   │   │   └── BRADESCO_21_02_2022__padrao_1__60746948000112__31122021__3c7c8a21.xlsx
│   │   │   ├── 60853942000144__VERALLIA_BRASIL_S.A/
│   │   │   │   └── VERALLIA_02_12_2022__padrao_1__60853942000144__31122021__570311a7.xlsx
│   │   │   ├── 60854833000141__BRAVOX_S_A_IND_E_COMERCIO_ELETRONICO/
│   │   │   │   └── BRAVOX_31072023__padrao_1__60854833000141__31122022__12277e4a.xlsx
│   │   │   ├── 60855574000173__ACUCAREIRA_QUATA_S_A/
│   │   │   │   └── ACUCAREIRA ZILOR 27032026__padrao_2__60855574000173__31032025__23a04d4c.xlsx
│   │   │   ├── 60856077000947__PAPIRUS_INDUSTRIA_DE_PAPEL_SA/
│   │   │   │   └── PAPIRUS RATING 25022026__padrao_2__60856077000947__31122024__c16ea95e.xlsx
│   │   │   ├── 60869336000117__CSN_CIMENTOS_BRASIL_S.A/
│   │   │   │   └── CSN CIMENTOS 08072025__padrao_1__60869336000117__31122024__d1a797bb.xlsx
│   │   │   ├── 60894730000105__USINAS_SIDERURGICAS_DE_MINAS_GERAIS_S_A._USIMINAS/
│   │   │   │   ├── USIMINAS 07072025__padrao_1__60894730000105__31122024__7f71a572.xlsx
│   │   │   │   └── USIMINAS 25062026__padrao_3__60894730000105__31122025__4d2af823.xlsx
│   │   │   ├── 60975737000151__SOCIEDADE_BENEFICENTE_SAO_CAMILO/
│   │   │   │   └── Grupo São Camilo 16_09_2022__padrao_1__60975737000151__31122021__1f25a956.xlsx
│   │   │   ├── 61064929000179__CORTEVA_AGRISCIENCE_DO_BRASIL_LTDA/
│   │   │   │   └── Corteva 15_08_2022__padrao_1__61064929000179__31122021__7142529d.xlsx
│   │   │   ├── 61067161000197__NADIR_FIGUEIREDO_S.A/
│   │   │   │   └── NADIR FIGUEIREDO 02042026__padrao_2__61067161000197__31122025__bb12f23d.xlsx
│   │   │   ├── 61082988000170__MARINGA_FERRO-LIGA_S.A/
│   │   │   │   ├── MARINGA FERRO LIGA 18062026__padrao_3__61082988000170__31122025__063a5587.xlsx
│   │   │   │   └── MARINGA FERRO LIGA 26082025__padrao_1__61082988000170__31122024__f481945d.xlsx
│   │   │   ├── 61092037000181__ETERNIT_S.A/
│   │   │   │   └── ETERNIT RATING 18122025__padrao_2__61092037000181__31122024__5f5b7005.xlsx
│   │   │   ├── 61101895000145__FÁBRICA_DE_PAPEL_SANTA_THEREZINHA_S.A/
│   │   │   │   └── Santher 01022024 sem eprotocolo__padrao_1__61101895000145__31122022__3432eec2.xlsx
│   │   │   ├── 61101895003918__SANTHER_-_FÁBRICA_DE_PAPEL_SANTA_THEREZINHA_S.A/
│   │   │   │   └── ficha SANTHER 2022-10__padrao_1__61101895003918__31122021__52885eed.xlsx
│   │   │   ├── 61144150000678__PADO_S_A/
│   │   │   │   └── PADO_28062023__padrao_1__61144150000678__31122022__a76a481b.xlsx
│   │   │   ├── 61186888000193__SPAL_INDUSTRIA_BRASILEIRA_DE_BEBIDAS_S_A/
│   │   │   │   └── COCA-COLA FEMSA RATING 25032026__padrao_2__61186888000193__31032025__60dcf530.xlsx
│   │   │   ├── 61186888000193__SPAL_INDÚSTRIA_BRASILEIRA_DE_BEBIDAS_S_A/
│   │   │   │   ├── Coca-cola FEMSA 05032024__padrao_1__61186888000193__5e08b655.xlsx
│   │   │   │   └── spal 05032024__padrao_1__61186888000193__31122022__e9e09a23.xlsx
│   │   │   ├── 61190096002136__EUROFARMA_LABORATÓRIOS_S.A/
│   │   │   │   └── EUROFARMA_03102023__padrao_1__61190096002136__31122022__80fe120d.xlsx
│   │   │   ├── 61409892000173__COMPANHIA_BRASILEIRA_DE_ALUMINIO/
│   │   │   │   ├── CBA 08102025 RATING RETIFICADO__padrao_2__61409892000173__bf5ce995.xlsx
│   │   │   │   ├── CBA 08102025__padrao_2__61409892000173__c4591776.xlsx
│   │   │   │   └── CBA 24062026__padrao_3__61409892000173__31122025__1c7d407b.xlsx
│   │   │   ├── 61409892000920__COMPANHIA_BRASILEIRA_DE_ALUMINIO/
│   │   │   │   └── CBA - Cia Brasileira de Alumínio 2022-07__padrao_1__61409892000920__31122021__c172740c.xlsx
│   │   │   ├── 61460325000141__UNIPAR_INDUPA_DO_BRASIL_S.A/
│   │   │   │   ├── INDUPA 19052026__padrao_2__61460325000141__31122025__ffa626f3.xlsx
│   │   │   │   └── INDUPA RATING 03112025__padrao_2__61460325000141__31122024__8f0380b7.xlsx
│   │   │   ├── 61486650000183__DIAGNOSTICOS_DA_AMERICA_S.A/
│   │   │   │   └── Diagnósticos da América 08042025__padrao_1__61486650000183__31122024__e10dd7b7.xlsx
│   │   │   ├── 61533949000141__S_A_O_ESTADO_DE_S.PAULO/
│   │   │   │   └── ESTADO DE SP 15_08_2022__padrao_1__61533949000141__31122021__b5284966.xlsx
│   │   │   ├── 61887899000109__INDEMIL_INDUSTRIA_E_COMERCIO_S_A/
│   │   │   │   ├── INDEMIL 27112024__padrao_1__61887899000109__31122023__b893dc0d.xlsx
│   │   │   │   └── INDEMIL RATING 23032026 - Copia__padrao_2__61887899000109__31122025__10310b50.xlsx
│   │   │   ├── 62070362000106__COMPANHIA_DO_METROPOLITANO_DE_SAO_PAULO/
│   │   │   │   └── Metrô São Paulo_06032023__padrao_1__62070362000106__31122021__6cf9d7ee.xlsx
│   │   │   ├── 62070362000106__COMPANHIA_DO_METROPOLITANO_DE_SAO_PAULO_-_METRO/
│   │   │   │   ├── METRO 15072025__padrao_1__62070362000106__31122024__08cd6789.xlsx
│   │   │   │   └── METRO SP 23062026__padrao_3__62070362000106__31122025__ced52235.xlsx
│   │   │   ├── 62258884000136__INTERCEMENT_BRASIL_S.A/
│   │   │   │   └── InterCement_20_10_2022__padrao_1__62258884000136__31122021__72cfc0b3.xlsx
│   │   │   ├── 62258884000136__INTERCEMENT_BRASIL_S_A_-_EM_RECUPERACAO_JUDICIAL/
│   │   │   │   ├── INTERCEMENT - 08072025__padrao_1__62258884000136__31122024__245958a9.xlsx
│   │   │   │   ├── INTERCEMENT RATING 13102025__padrao_2__62258884000136__fc328776.xlsx
│   │   │   │   └── INTERCEMENT RATING 19032026__padrao_2__62258884000136__31122025__35e8eca2.xlsx
│   │   │   ├── 62473004000144__BIOAGRI_LABORATORIOS_LTDA/
│   │   │   │   └── Bioagri Laboratórios_03-10-2022__padrao_1__62473004000144__31122021__dc2cc2a7.xlsx
│   │   │   ├── 62545686000153__OXITENO_S_A_INDUSTRIA_E_COMERCIO/
│   │   │   │   └── OXITENO 24062026__padrao_3__62545686000153__31122025__a3c848b4.xlsx
│   │   │   ├── 62695036000194__EVONIK_BRASIL_LTDA/
│   │   │   │   ├── EVONIK 04112024__padrao_1__62695036000194__31122023__92ca6f26.xlsx
│   │   │   │   ├── EVONIK 13082025__padrao_1__62695036000194__31122024__1dec7ef6.xlsx
│   │   │   │   ├── EVONIK 29052026__padrao_2__62695036000194__31122025__3d99e03b.xlsx
│   │   │   │   └── EVONIK_16062023__padrao_1__62695036000194__31122022__0133c528.xlsx
│   │   │   ├── 62695036005404__EVONIK_BRASIL_LTDA/
│   │   │   │   └── EVONIK_FILIAL 04112024__padrao_1__62695036005404__31122023__c19ec17f.xlsx
│   │   │   ├── 65882680000160__TEREOS_AMIDO_E_ADOCANTES_BRASIL_S.A/
│   │   │   │   └── TEREOS AMIDOS E ADOCANTES RATING 2711202__padrao_2__65882680000160__31122025__d468ff74.xlsx
│   │   │   ├── 67620377000114__MINERVA_S.A/
│   │   │   │   └── Minerva 01112023__padrao_1__67620377000114__31122022__44534d17.xlsx
│   │   │   ├── 71832679000123__COMPANHIA_PAULISTA_DE_TRENS_METROPOLITANOS_-_CPTM/
│   │   │   │   ├── CPTM 21072025__padrao_1__71832679000123__31122024__11a79b71.xlsx
│   │   │   │   └── CPTM 25062026__padrao_3__71832679000123__31122025__2b863724.xlsx
│   │   │   ├── 73856593000166__PRATI,_DONADUZZI_&_CIA_LTDA/
│   │   │   │   ├── PRATI DONADUZI 14072026__padrao_3__73856593000166__31122025__4d2d6a89.xlsx
│   │   │   │   ├── PRATI DONADUZZI 24082023__padrao_1__73856593000166__31122022__814e04eb.xlsx
│   │   │   │   └── Prati Donaduzzi_24_06_2022__padrao_1__73856593000166__31122021__bc11dfc1.xlsx
│   │   │   ├── 75084871000130__COOPERVAL_COOPERATIVA_AGROINDUSTRIAL_VALE_DO_IVAÍ_LTDA/
│   │   │   │   └── COOPERVAL 14072026__padrao_3__75084871000130__31122025__7ad8dbf1.xlsx
│   │   │   ├── 75222224000147__UNIMED_DE_LONDRINA_COOPERATIVA_DE_TRABALHO_MEDICO/
│   │   │   │   └── UNIMED LONDRINA__padrao_3__75222224000147__31122025__0c3aa35f.xlsx
│   │   │   ├── 75904383000121__COAMO_AGROINDUSTRIAL_COOPERATIVA/
│   │   │   │   ├── COAMO 02062025__padrao_1__75904383000121__31122024__0eda9770.xlsx
│   │   │   │   └── COAMO 11012024__padrao_1__75904383000121__31122022__a6ce8adf.xlsx
│   │   │   ├── 76081892000164__HOSPITAL_POLICLINICA_CASCAVEL_S.A/
│   │   │   │   └── Hospital Policlina Cascavel 2023-01-26__padrao_1__76081892000164__31122021__58119da9.xlsx
│   │   │   ├── 76093731000190__COPACOL-COOPERATIVA_AGROINDUSTRIAL_CONSOLATA/
│   │   │   │   ├── COPACOL 18082023__padrao_1__76093731000190__31122022__fab51e04.xlsx
│   │   │   │   ├── COPACOL_25_08_2022 - 1__padrao_1__76093731000190__31122021__59299aa7.xlsx
│   │   │   │   └── ELEKEIROZ 15052024__padrao_1__76093731000190__31122023__d921eda6.xlsx
│   │   │   ├── 76093731000190__COPACOL_-_COOPERATIVA_AGROINDUSTRIAL_CONSOLATA/
│   │   │   │   └── COPACOL 19082026__padrao_3__76093731000190__31122025__4865a910.xlsx
│   │   │   ├── 76093731002649__COPACOL-COOPERATIVA_AGROINDUSTRIAL_CONSOLATA/
│   │   │   │   └── COPACOL RATING 24102025__padrao_2__76093731002649__2b64b089.xlsx
│   │   │   ├── 76093731008256__COPACOL-COOPERATIVA_AGROINDUSTRIAL_CONSOLATA/
│   │   │   │   └── COPACOL_25_08_2022 - 2__padrao_1__76093731008256__31122021__ec69b1dd.xlsx
│   │   │   ├── 76098219000137__COOPAVEL_COOPERATIVA_AGROINDUSTRIAL/
│   │   │   │   ├── COOPAVEL 11012024__padrao_1__76098219000137__31122022__e5e5322d.xlsx
│   │   │   │   └── COPAVEL RATING 11112025__padrao_2__76098219000137__31122024__4d442061.xlsx
│   │   │   ├── 76107770000108__FRISIA_COOPERATIVA_AGROINDUSTRIAL/
│   │   │   │   └── FRISIA_03102023__padrao_1__76107770000108__31122022__1c5519c3.xlsx
│   │   │   ├── 76208867000107__MUNICIPIO_DE_CASCAVEL/
│   │   │   │   └── PM Cascavel__padrao_1__76208867000107__31122021__5e9d5c16.xlsx
│   │   │   ├── 76430438000171__IRMAOS_MUFFATO_S.A/
│   │   │   │   └── Muffato 07112023__padrao_1__76430438000171__31122022__ea45a7d0.xlsx
│   │   │   ├── 76484013000145__COMPANHIA_DE_SANEAMENTO_DO_PARANA_SANEPAR/
│   │   │   │   ├── SANEPAR 02072025__padrao_1__76484013000145__31122024__267c8562.xlsx
│   │   │   │   ├── SANEPAR 12012024__padrao_1__76484013000145__31122022__72666602.xlsx
│   │   │   │   ├── SANEPAR 21052026__padrao_2__76484013000145__31122025__20cbb585.xlsx
│   │   │   │   └── SANEPAR RATING 17102025__padrao_2__76484013000145__0aa103a9.xlsx
│   │   │   ├── 76493626000149__CLUBE_CURITIBANO/
│   │   │   │   └── CLUBE CURITIBANO 06052026__padrao_2__76493626000149__31102025__7d13fd21.xlsx
│   │   │   ├── 76518836000144__ARAUCO_DO_BRASIL_S.A/
│   │   │   │   └── ficha ARAUCO 2022__padrao_1__76518836000144__31122020__42324b70.xlsx
│   │   │   ├── 76591569000130__ASSOCIACAO_HOSPITALAR_DE_PROT_INFANCIA_DR_RAUL_CARNEIRO/
│   │   │   │   └── Hospital Pequeno Principe 29_09_2022__padrao_1__76591569000130__31122021__97825977.xlsx
│   │   │   ├── 76610062000187__INCEPA_REVESTIMENTOS_CERAMICOS_LTDA/
│   │   │   │   └── Incepa 20052024__padrao_1__76610062000187__1aab925d.xlsx
│   │   │   ├── 76630573000160__CIA_DE_CIMENTO_ITAMBE/
│   │   │   │   ├── CIMENTO ITAMBE 27_07_2022__padrao_1__76630573000160__31122021__ca039cd0.xlsx
│   │   │   │   ├── Itambe 03042024__padrao_1__76630573000160__31122023__685e7c5e.xlsx
│   │   │   │   ├── ITAMBE CIMENTOS 24072026__padrao_3__76630573000160__31122025__752f27cc.xlsx
│   │   │   │   └── ITAMBE ENERGETICA SA 18082025__padrao_1__76630573000160__31122024__f03e61f1.xlsx
│   │   │   ├── 76827344000130__CIA_CANOINHAS_DE_PAPEL/
│   │   │   │   └── CANOINHAS 17072025__padrao_1__76827344000130__31122024__2e26b796.xlsx
│   │   │   ├── 77595395000147__FRIMESA_COOPERATIVA_CENTRAL/
│   │   │   │   └── FRIMESA - 08 04 2024__padrao_1__77595395000147__31122023__f0d68a94.xlsx
│   │   │   ├── 77752293000198__LAR_COOPERATIVA_AGROINDUSTRIAL/
│   │   │   │   ├── LAR COOPERATIVA 03072025__padrao_1__77752293000198__31122024__af80c124.xlsx
│   │   │   │   └── LAR COOPERATIVA 07012024 v2__padrao_1__77752293000198__31122023__05b53361.xlsx
│   │   │   ├── 77781706000243__UNIMED_PONTA_GROSSA_COOPERATIVA_DE_TRABALHO_MÉDICO/
│   │   │   │   └── UNIMED 15072026__padrao_3__77781706000243__31122025__31b53d33.xlsx
│   │   │   ├── 77863223000107__C.VALE_-_COOPERATIVA_AGROINDUSTRIAL/
│   │   │   │   └── CVALE_09032023__padrao_1__77863223000107__31122021__9e31b9e6.xlsx
│   │   │   ├── 77863223004366__C.VALE_-_COOPERATIVA_AGROINDUSTRIAL/
│   │   │   │   └── C. VALE RATING 07112025__padrao_2__77863223004366__31122024__efc27454.xlsx
│   │   │   ├── 77863223017930__C.VALE_-_COOPERATIVA_AGROINDUSTRIAL/
│   │   │   │   └── C. VALE 25052026__padrao_2__77863223017930__31122025__7eea2bb3.xlsx
│   │   │   ├── 77887917000184__SANTA_MARIA_CIA_DE_PAPEL_E_CELULOSE/
│   │   │   │   └── Santa Maria_11_03_2022__padrao_1__77887917000184__31122021__9349f339.xlsx
│   │   │   ├── 77890846000179__COOPERATIVA_AGRARIA_AGROINDUSTRIAL/
│   │   │   │   └── Cooperativa AGRARIA 28032024__padrao_1__77890846000179__31122022__60bf71bf.xlsx
│   │   │   ├── 77964393000188__TECPAR-_INSTITUTO_DE_TECNOLOGIA_DO_PARANÁ/
│   │   │   │   └── TECPAR 03072024__padrao_1__77964393000188__01042024__853f15d0.xlsx
│   │   │   ├── 78613841000161__ASSOCIAÇÃO_EVANGÉLICA_BENEFICENTE_DE_LONDRINA/
│   │   │   │   └── HOSPITAL EVANLEGICO DE LONDRINA 20072026__padrao_3__78613841000161__31122025__af0f784d.xlsx
│   │   │   ├── 78908266000124__MILI_S_A/
│   │   │   │   ├── FICHA_CONSUMIDORES_MILI_SA_PREENCHIDA__padrao_3__78908266000124__31122025__e554d79b.xlsx
│   │   │   │   └── MILI RATING 19112025__padrao_2__78908266000124__31122024__f36c7985.xlsx
│   │   │   ├── 79109237000165__SANTA_TEREZINHA_PARTICIPACOES_S_A/
│   │   │   │   └── Santa Terezinha 24032025__padrao_1__79109237000165__31122024__edf2b7ad.xlsx
│   │   │   ├── 79114450000165__COCAMAR_COOPERATIVA_AGROINDUSTRIAL/
│   │   │   │   ├── Cocamar 01022024 sem eprotocolo__padrao_1__79114450000165__31122022__f8455706.xlsx
│   │   │   │   ├── COCAMAR 27-04-2026__padrao_2__79114450000165__31122025__bea30380.xlsx
│   │   │   │   └── Cocamar 28022024__padrao_1__79114450000165__31122023__708fb770.xlsx
│   │   │   ├── 79114450001480__COCAMAR_COOPERATIVA_AGROINDUSTRIAL/
│   │   │   │   └── COCAMAR 11012024__padrao_1__79114450001480__31122022__7e1bfc50.xlsx
│   │   │   ├── 79379491000183__HAVAN_S.A/
│   │   │   │   ├── HAVAN - 08082025__padrao_1__79379491000183__31122024__6ab8b107.xlsx
│   │   │   │   └── HAVAN SA 06042026__padrao_2__79379491000183__31122025__523419f3.xlsx
│   │   │   ├── 79763884000196__BARIGUI_VEICULOS_LTDA/
│   │   │   │   └── Grupo Barigui 05_09_2022__padrao_1__79763884000196__31122021__54250ddf.xlsx
│   │   │   ├── 79863569000130__COASUL_COOPERATIVA_AGROINDUSTRIAL/
│   │   │   │   └── COASUL RATING 31102025__padrao_2__79863569000130__31122024__f81d96ad.xlsx
│   │   │   ├── 81270548000153__UNIAO_OESTE_PARANAENSE_DE_ESTUDOS_E_COMBATE_AO_CANCER/
│   │   │   │   └── UNIAO OESTE 20052026__padrao_2__81270548000153__31122025__952a4896.xlsx
│   │   │   ├── 81716219000193__MOINHO_ITAIPU_S_A/
│   │   │   │   └── Moinho Itaipu 29062025__padrao_1__81716219000193__31122024__40d11e9f.xlsx
│   │   │   ├── 81905176000194__BERNECK_S.A._PAINEIS_E_SERRADOS/
│   │   │   │   ├── BERNECK 03072025__padrao_1__81905176000194__31122024__320a78ac.xlsx
│   │   │   │   └── BERNECK 08102025__padrao_2__81905176000194__6e0a6a6c.xlsx
│   │   │   ├── 82196510000140__REPINHO_REFLORESTADORA_MADEIRAS_E_COMPENSADOS_LTDA/
│   │   │   │   ├── REPINHO 01072025__padrao_1__82196510000140__31122024__e76ed1e4.xlsx
│   │   │   │   └── REPINHO 29042025__padrao_1__82196510000140__31122023__b9f41461.xlsx
│   │   │   ├── 82295817000107__NITAPLAST_IND_E_COM_DE_PLASTICOS_INDUSTRIAIS_LTDA/
│   │   │   │   └── Nitaplast 16_08_2022__padrao_1__82295817000107__31122021__889001c2.xlsx
│   │   │   ├── 82640558000104__KARSTEN_S.A/
│   │   │   │   ├── KARSTEN - 15.07.2024__padrao_1__82640558000104__31122023__60926115.xlsx
│   │   │   │   ├── Karsten 12_09_2022__padrao_1__82640558000104__31122021__c27c6ec1.xlsx
│   │   │   │   └── KARSTEN SA 09102025__padrao_2__82640558000104__b0eb3c66.xlsx
│   │   │   ├── 83305235000119__COOPERATIVA_AGROINDUSTRIAL_ALFA/
│   │   │   │   └── COOPERALFA 27052026__padrao_2__83305235000119__31122025__0901b7a9.xlsx
│   │   │   ├── 83310441000117__COOPERATIVA_CENTRAL_AURORA_ALIMENTOS/
│   │   │   │   ├── AURORA 10082023__padrao_1__83310441000117__31122022__b9308554.xlsx
│   │   │   │   └── AURORA ALIMENTOS 20072026__padrao_3__83310441000117__31122025__6ca5d965.xlsx
│   │   │   ├── 83647990000181__COOPERATIVA_ALIANCA/
│   │   │   │   ├── COOPERALIANCA 11012024__padrao_1__83647990000181__31122022__613b9d5c.xlsx
│   │   │   │   └── COOPERALIANÇA 01102024__padrao_1__83647990000181__31122023__c8a99632.xlsx
│   │   │   ├── 83731927000129__COOPERATIVA_REGIONAL_AURIVERDE/
│   │   │   │   └── COOPERATIVA REGIONAL AURIVERDE RATING 12__padrao_2__83731927000129__31122025__9305e149.xlsx
│   │   │   ├── 84046101000193__BUNGE_ALIMENTOS_S.A/
│   │   │   │   └── BUNGE 18062026__padrao_3__84046101000193__31122025__d1fcb09a.xlsx
│   │   │   ├── 84046101000193__BUNGE_ALIMENTOS_S_A/
│   │   │   │   └── BUNGE 09102025__padrao_2__84046101000193__e9800550.xlsx
│   │   │   ├── 84683374000149__TUPY_S_A/
│   │   │   │   ├── TUPY 14072025__padrao_1__84683374000149__31122024__0f77b00a.xlsx
│   │   │   │   └── TUPY_15052023__padrao_1__84683374000149__31122021__302cbbb9.xlsx
│   │   │   ├── 84684455000163__TIGRE_S.A._PARTICIPACOES/
│   │   │   │   └── TIGRE_27032023__padrao_1__84684455000163__31122021__ec8b81af.xlsx
│   │   │   ├── 84693183000168__SCHULZ_S_A/
│   │   │   │   └── SCHULZ 18082026__padrao_3__84693183000168__31122025__4d8afcb7.xlsx
│   │   │   ├── 84709955000102__CIA_INDUSTRIAL_H._CARLOS_SCHNEIDER/
│   │   │   │   └── CISER 11092025__padrao_1__84709955000102__31122024__039e81e8.xlsx
│   │   │   ├── 85070068000108__GONCALVES_&_TORTOLA_S_A/
│   │   │   │   └── GTFOODS 15072026__padrao_3__85070068000108__31122025__9cdf4f86.xlsx
│   │   │   ├── 85070068000108__GRUPO_GTFOODS/
│   │   │   │   └── GTFOODS 00354264__padrao_1__85070068000108__31122024__81e96500.xlsx
│   │   │   ├── 85090033000122__JAGUAFRANGOS_INDUSTRIA_E_COMERCIO_DE_ALIMENTOS_LTDA/
│   │   │   │   └── JAGUAFRANGOS 08012024__padrao_1__85090033000122__31122022__fe546df1.xlsx
│   │   │   ├── 85937316000167__RESERVA_DE_LUCROS/
│   │   │   │   ├── CEESAM 11-12-2025__padrao_2__85937316000167__31122024__67ab82b3.xlsx
│   │   │   │   └── FICHA_CONSUMIDORES_V1_CEESAM_PREENCHIDA __padrao_3__85937316000167__31122025__2485a794.xlsx
│   │   │   ├── 86046414000177__FIACAO_SAO_BENTO_SA/
│   │   │   │   └── Fiação São Bento 08_11_2022__padrao_1__86046414000177__31122021__f350f198.xlsx
│   │   │   ├── 87547170000179__TODESCHINI_SA_INDUSTRIA_E_COMERCIO/
│   │   │   │   └── Brastex - Avaliação Middle__padrao_1__87547170000179__31122021__42c15430.xlsx
│   │   │   ├── 87776043000141__COOPERATIVA_DE_ELETRIFICACAO_CENTRO_JACUI_LTDA/
│   │   │   │   └── CELETRO 08072026__padrao_3__87776043000141__31122025__cdacef6e.xlsx
│   │   │   ├── 87870952000144__BORRACHAS_VIPAL_S.A/
│   │   │   │   └── VIPAL_05042023__padrao_1__87870952000144__31122022__33c3c759.xlsx
│   │   │   ├── 89086144001198__RANDON_SA_IMPLEMENTOS_E_PARTICIPACOES/
│   │   │   │   └── RANDON 04032024__padrao_1__89086144001198__31122022__4d9d311c.xlsx
│   │   │   ├── 89086144001198__RANDONCORP_S.A/
│   │   │   │   └── RANDON 03082026__padrao_3__89086144001198__31122025__bc641aaf.xlsx
│   │   │   ├── 89096457000155__SLC_AGRICOLA_S.A/
│   │   │   │   └── SLC_AGRICOLA_23_11_2022__padrao_1__89096457000155__31122021__f94f457d.xlsx
│   │   │   ├── 89637490000145__CNEP_-_CADASTRO_NACIONAL_DE_EMPRESAS_PUNIDAS/
│   │   │   │   └── Klabin 03112023__padrao_2__89637490000145__ecc4e69a.xlsx
│   │   │   ├── 89637490000145__KLABIN_S.A/
│   │   │   │   ├── Klabin 12062024__padrao_1__89637490000145__31122023__38f77c59.xlsx
│   │   │   │   ├── KLABIN 15052026__padrao_2__89637490000145__31122025__336078de.xlsx
│   │   │   │   ├── KLABIN 18_02_2022__padrao_1__89637490000145__31122021__43b7c8fe.xlsx
│   │   │   │   └── Klabin 26032025__padrao_1__89637490000145__31122024__95b78736.xlsx
│   │   │   ├── 89850341000160__GRENDENE_S_A/
│   │   │   │   └── Grendene 2022-07-28__padrao_1__89850341000160__31122021__77d7af6b.xlsx
│   │   │   ├── 90660754000160__COPREL_COOPERATIVA_DE_ENERGIA/
│   │   │   │   └── COPREL 18082026__padrao_3__90660754000160__31122025__dafc322e.xlsx
│   │   │   ├── 91495499000100__STARA_S.A._-_INDUSTRIA_DE_IMPLEMENTOS_AGRICOLAS/
│   │   │   │   └── Stara - Avaliação Middle__padrao_1__91495499000100__31122021__f7a75664.xlsx
│   │   │   ├── 91950261000128__CRELUZ_-_COOPERATIVA_DE_DISTRIBUICAO_DE_ENERGIA/
│   │   │   │   └── CRELUZ_09102024__padrao_1__91950261000128__31122023__6ea1af09.xlsx
│   │   │   ├── 92091891000157__ASUN_COMERCIO_DE_GENEROS_ALIMENTICIOS_LTDA/
│   │   │   │   └── ASUN RATING 24102025__padrao_2__92091891000157__3a856968.xlsx
│   │   │   ├── 92660604000182__YARA_BRASIL_FERTILIZANTES_S_A/
│   │   │   │   └── ficha Yara Brasil Fertilizantes SA 2022__padrao_1__92660604000182__31122021__466d79b7.xlsx
│   │   │   ├── 92660604016933__YARA_BRASIL_FERTILIZANTES_S_A/
│   │   │   │   └── YARA NITROGENADOS RATING 11112025__padrao_2__92660604016933__31122024__d03ac06a.xlsx
│   │   │   ├── 92685833000151__ASSOCIACAO_HOSPITALAR_MOINHOS_DE_VENTO/
│   │   │   │   └── Hospital Moinhos de Vento 22_09_2022__padrao_1__92685833000151__31122021__307aba69.xlsx
│   │   │   ├── 92791243000103__IRANI_PAPEL_E_EMBALAGEM_S.A/
│   │   │   │   └── IRANI_07-07-2022__padrao_1__92791243000103__31122021__d0bf138c.xlsx
│   │   │   ├── 92802784000190__COMPANHIA_RIOGRANDENSE_DE_SANEAMENTO_-_CORSAN/
│   │   │   │   ├── COMPANHIA RIOGRANDENSE DE SANEAMENTO 180__padrao_1__92802784000190__31122024__4afe409f.xlsx
│   │   │   │   └── FICHA_CONSUMIDORES_CORSAN_PREENCHIDA__padrao_3__92802784000190__31122025__c1382859.xlsx
│   │   │   ├── 93586303000119__VIBRA_AGROINDUSTRIAL_S.A/
│   │   │   │   └── VIBRA 26.07.2024__padrao_1__93586303000119__31122023__11f9c65f.xlsx
│   │   │   ├── 93586303000119__VIBRA_AGROINDUSTRILA_S.A/
│   │   │   │   └── VIBRA_05092025__padrao_1__93586303000119__31122024__58615936.xlsx
│   │   │   ├── 95824322000161__RESERVA_DE_LUCROS/
│   │   │   │   └── COOPERLUZ 14082026__padrao_3__95824322000161__31122025__5be92039.xlsx
│   │   │   ├── 97081434000103__RESERVA_DE_LUCROS/
│   │   │   │   └── CERMISSOES 17082026__padrao_3__97081434000103__31122025__2dfffde5.xlsx
│   │   │   ├── 97837181000147__DEXCO_S.A/
│   │   │   │   ├── DEXCO - 15.07.2024__padrao_1__97837181000147__31122023__3b6dae11.xlsx
│   │   │   │   ├── DEXCO 14072025__padrao_1__97837181000147__31122024__87e6f734.xlsx
│   │   │   │   ├── DEXCO 22062026__padrao_3__97837181000147__31122025__b8a32904.xlsx
│   │   │   │   ├── DEXCO S.A._30-06-2022__padrao_1__97837181000147__31122021__60b32cbd.xlsx
│   │   │   │   └── DEXCO_28032023__padrao_1__97837181000147__31122022__4a186fc9.xlsx
│   │   │   ├── 97839922000129__COOPERATIVA_REGIONAL_DE_ENERGIA_TAQUARI_JACUI/
│   │   │   │   └── CERTAJA 12082026__padrao_3__97839922000129__31122025__24d1f334.xlsx
│   │   │   └── 98042963000152__COOPERATIVA_DE_DISTRIBUICAO_DE_ENERGIA_ENTRE_RIOS_LTDA/
│   │   │       └── CERTHIL 17082026__padrao_3__98042963000152__31122025__16197e42.xlsx
│   │   ├── ingestion_log/
│   │   │   ├── fichas_comercializadoras_ingestion.jsonl
│   │   │   └── fichas_consumidores_ingestion.jsonl
│   │   ├── mtm_raw/
│   │   ├── receita_raw/
│   │   ├── risk3_raw/
│   │   │   ├── risk3_00000569605903_20260902_094616.json
│   │   │   ├── risk3_00001180000126_20260902_094618.json
│   │   │   ├── risk3_00007750000195_20260902_094618.json
│   │   │   ├── risk3_00056633000111_20260902_094619.json
│   │   │   ├── risk3_00064742000180_20260902_094620.json
│   │   │   ├── risk3_00071815000161_20260902_094621.json
│   │   │   ├── risk3_00080671000100_20260902_094622.json
│   │   │   ├── risk3_00111960000129_20260902_094623.json
│   │   │   ├── risk3_00178840000149_20260902_134320.json
│   │   │   ├── risk3_00212305000167_20260902_094645.json
│   │   │   ├── risk3_00246872000134_20260902_094646.json
│   │   │   ├── risk3_00257348000169_20260902_094647.json
│   │   │   ├── risk3_00262371000575_20260902_094648.json
│   │   │   ├── risk3_00298749000167_20260902_094657.json
│   │   │   ├── risk3_00301560000186_20260902_094658.json
│   │   │   ├── risk3_00314794000168_20260902_094659.json
│   │   │   ├── risk3_00336754000117_20260902_094700.json
│   │   │   ├── risk3_00339244000101_20260902_094700.json
│   │   │   ├── risk3_00350242000105_20260902_094701.json
│   │   │   ├── risk3_00350763002297_20260902_094702.json
│   │   │   ├── risk3_00359256000190_20260902_094703.json
│   │   │   ├── risk3_00366257000161_20260902_094704.json
│   │   │   ├── risk3_00374121000101_20260902_094705.json
│   │   │   ├── risk3_00395490000172_20260902_094706.json
│   │   │   ├── risk3_00412182000108_20260902_094706.json
│   │   │   ├── risk3_00457993000125_20260902_094707.json
│   │   │   ├── risk3_00464830000684_20260902_094708.json
│   │   │   ├── risk3_00465813000408_20260902_094709.json
│   │   │   ├── risk3_00495545000116_20260902_094710.json
│   │   │   ├── risk3_00496586000127_20260902_094710.json
│   │   │   ├── risk3_00508070000155_20260902_094711.json
│   │   │   ├── risk3_00514820000100_20260902_094712.json
│   │   │   ├── risk3_00529188000160_20260902_094713.json
│   │   │   ├── risk3_00552646000181_20260902_094714.json
│   │   │   ├── risk3_00568480000191_20260902_094715.json
│   │   │   ├── risk3_00573283000160_20260902_094715.json
│   │   │   ├── risk3_00583224000173_20260902_094716.json
│   │   │   ├── risk3_00601731000192_20260902_094717.json
│   │   │   ├── risk3_00605582000130_20260902_094718.json
│   │   │   ├── risk3_00662514000102_20260902_094719.json
│   │   │   ├── risk3_00668630000139_20260902_094719.json
│   │   │   ├── risk3_00671047000187_20260902_094720.json
│   │   │   ├── risk3_00717453000133_20260902_094721.json
│   │   │   ├── risk3_00727465000149_20260902_094722.json
│   │   │   ├── risk3_00729422000100_20260902_094723.json
│   │   │   ├── risk3_00750846000149_20260902_094724.json
│   │   │   ├── risk3_00767659000178_20260902_094725.json
│   │   │   ├── risk3_00776574000660_20260902_094726.json
│   │   │   ├── risk3_00807422000173_20260902_094726.json
│   │   │   ├── risk3_00822488000132_20260902_094727.json
│   │   │   ├── risk3_00829352000154_20260902_094728.json
│   │   │   ├── risk3_00831245000160_20260902_094732.json
│   │   │   ├── risk3_00863529000139_20260902_094733.json
│   │   │   ├── risk3_00868626000114_20260902_094734.json
│   │   │   ├── risk3_00869496000134_20260902_094734.json
│   │   │   ├── risk3_00890837000153_20260902_094735.json
│   │   │   ├── risk3_00893913000265_20260902_094736.json
│   │   │   ├── risk3_00899825000190_20260902_094737.json
│   │   │   ├── risk3_00931787000105_20260902_094738.json
│   │   │   ├── risk3_00979768000159_20260902_094738.json
│   │   │   ├── risk3_00993264000193_20260902_094739.json
│   │   │   ├── risk3_00993264008097_20260902_094740.json
│   │   │   ├── risk3_01015553000180_20260902_094741.json
│   │   │   ├── risk3_01019449000164_20260902_094742.json
│   │   │   ├── risk3_01069573000134_20260902_094743.json
│   │   │   ├── risk3_01105236000155_20260902_094743.json
│   │   │   ├── risk3_01125487000100_20260902_094744.json
│   │   │   ├── risk3_01152790000193_20260902_094745.json
│   │   │   ├── risk3_01191198000109_20260902_094746.json
│   │   │   ├── risk3_01198813000109_20260902_094747.json
│   │   │   ├── risk3_01203549000227_20260902_094747.json
│   │   │   ├── risk3_01225953000110_20260902_094748.json
│   │   │   ├── risk3_01257995000133_20260902_094749.json
│   │   │   ├── risk3_01261681000104_20260902_094750.json
│   │   │   ├── risk3_01274980000183_20260902_094751.json
│   │   │   ├── risk3_01304124000123_20260902_094752.json
│   │   │   ├── risk3_01304124001790_20260902_094753.json
│   │   │   ├── risk3_01304136000158_20260902_094753.json
│   │   │   ├── risk3_01333984000195_20260902_094754.json
│   │   │   ├── risk3_01354988000150_20260902_094755.json
│   │   │   ├── risk3_01377961000182_20260902_094756.json
│   │   │   ├── risk3_01397555000181_20260902_094757.json
│   │   │   ├── risk3_01417701000193_20260902_094757.json
│   │   │   ├── risk3_01445875000160_20260902_094758.json
│   │   │   ├── risk3_01485633000108_20260902_094759.json
│   │   │   ├── risk3_01525323000161_20260902_094800.json
│   │   │   ├── risk3_01581464000100_20260902_094801.json
│   │   │   ├── risk3_01594992000195_20260902_094802.json
│   │   │   ├── risk3_01618551000267_20260902_094803.json
│   │   │   ├── risk3_01682147000171_20260902_094804.json
│   │   │   ├── risk3_01691944000204_20260902_094804.json
│   │   │   ├── risk3_01693497000133_20260902_094805.json
│   │   │   ├── risk3_01712320000137_20260902_094806.json
│   │   │   ├── risk3_01715975000169_20260902_094807.json
│   │   │   ├── risk3_01785345000160_20260902_094808.json
│   │   │   ├── risk3_01794540000157_20260902_094809.json
│   │   │   ├── risk3_01831188000182_20260902_094810.json
│   │   │   ├── risk3_01886356000137_20260902_094810.json
│   │   │   ├── risk3_01912239000109_20260902_094812.json
│   │   │   ├── risk3_01947943000199_20260902_094813.json
│   │   │   ├── risk3_01966329000174_20260902_094814.json
│   │   │   ├── risk3_01974675000102_20260902_094815.json
│   │   │   ├── risk3_02081239000169_20260902_094816.json
│   │   │   ├── risk3_02103847000127_20260902_094816.json
│   │   │   ├── risk3_02122913000106_20260902_094817.json
│   │   │   ├── risk3_02135888000103_20260902_094818.json
│   │   │   ├── risk3_02163440000195_20260902_094819.json
│   │   │   ├── risk3_02179949000126_20260902_094820.json
│   │   │   ├── risk3_02202020000170_20260902_094820.json
│   │   │   ├── risk3_02224840000163_20260902_094821.json
│   │   │   ├── risk3_02227579000155_20260902_094822.json
│   │   │   ├── risk3_02248827000144_20260902_094823.json
│   │   │   ├── risk3_02266644000151_20260902_094824.json
│   │   │   ├── risk3_02279324000136_20260902_094825.json
│   │   │   ├── risk3_02305606000160_20260902_094826.json
│   │   │   ├── risk3_02332686000143_20260902_094827.json
│   │   │   ├── risk3_02335262000132_20260902_094828.json
│   │   │   ├── risk3_02341494000101_20260902_094830.json
│   │   │   ├── risk3_02343359000197_20260902_094831.json
│   │   │   ├── risk3_02357251000153_20260902_094831.json
│   │   │   ├── risk3_02370462000126_20260902_094832.json
│   │   │   ├── risk3_02446766000120_20260902_094833.json
│   │   │   ├── risk3_02459413000164_20260902_094834.json
│   │   │   ├── risk3_02460752000160_20260902_094835.json
│   │   │   ├── risk3_02468496000158_20260902_094836.json
│   │   │   ├── risk3_02476067000122_20260902_094837.json
│   │   │   ├── risk3_02476790000101_20260902_094838.json
│   │   │   ├── risk3_02497408000146_20260902_094838.json
│   │   │   ├── risk3_02501470000164_20260902_094839.json
│   │   │   ├── risk3_02513991000131_20260902_094841.json
│   │   │   ├── risk3_02529745000178_20260902_094842.json
│   │   │   ├── risk3_02529745000259_20260902_094843.json
│   │   │   ├── risk3_02560932000114_20260902_094843.json
│   │   │   ├── risk3_02561851000139_20260902_094844.json
│   │   │   ├── risk3_02562006000188_20260902_094845.json
│   │   │   ├── risk3_02583678000170_20260902_094846.json
│   │   │   ├── risk3_02591442000185_20260902_094847.json
│   │   │   ├── risk3_02634644000167_20260902_094848.json
│   │   │   ├── risk3_02679497000141_20260902_094849.json
│   │   │   ├── risk3_02691745000170_20260902_094850.json
│   │   │   ├── risk3_02725300000163_20260902_094850.json
│   │   │   ├── risk3_02740399000172_20260902_094852.json
│   │   │   ├── risk3_02744832000148_20260902_094853.json
│   │   │   ├── risk3_02749435000169_20260902_094854.json
│   │   │   ├── risk3_02788151000181_20260902_094855.json
│   │   │   ├── risk3_02794165000108_20260902_094856.json
│   │   │   ├── risk3_02795010000196_20260902_094856.json
│   │   │   ├── risk3_02831172000132_20260902_094857.json
│   │   │   ├── risk3_02845645000150_20260902_094858.json
│   │   │   ├── risk3_02876495000142_20260902_094859.json
│   │   │   ├── risk3_02883512000179_20260902_094900.json
│   │   │   ├── risk3_02886685000140_20260902_094901.json
│   │   │   ├── risk3_02898246000158_20260902_094902.json
│   │   │   ├── risk3_02916265000160_20260902_094903.json
│   │   │   ├── risk3_02916265037322_20260902_094909.json
│   │   │   ├── risk3_02917571000110_20260902_094910.json
│   │   │   ├── risk3_02921346000158_20260902_094911.json
│   │   │   ├── risk3_02929563000194_20260902_094912.json
│   │   │   ├── risk3_02937632000101_20260902_094912.json
│   │   │   ├── risk3_02948278000110_20260902_094913.json
│   │   │   ├── risk3_02995367000118_20260902_094914.json
│   │   │   ├── risk3_02995385000108_20260902_094915.json
│   │   │   ├── risk3_03004238000183_20260902_094916.json
│   │   │   ├── risk3_03058653000110_20260902_094918.json
│   │   │   ├── risk3_03058852000128_20260902_094919.json
│   │   │   ├── risk3_03061685000174_20260902_094920.json
│   │   │   ├── risk3_03084476000146_20260902_094921.json
│   │   │   ├── risk3_03109168000128_20260902_094922.json
│   │   │   ├── risk3_03121295000142_20260902_094922.json
│   │   │   ├── risk3_03135376000100_20260902_094923.json
│   │   │   ├── risk3_03156784000130_20260902_094924.json
│   │   │   ├── risk3_03270248000160_20260902_094925.json
│   │   │   ├── risk3_03282398000194_20260902_094926.json
│   │   │   ├── risk3_03298956000100_20260902_094927.json
│   │   │   ├── risk3_03304180000193_20260902_094927.json
│   │   │   ├── risk3_03315918000541_20260902_094928.json
│   │   │   ├── risk3_03391986000166_20260902_094929.json
│   │   │   ├── risk3_03400446000100_20260902_094930.json
│   │   │   ├── risk3_03402181000170_20260902_094931.json
│   │   │   ├── risk3_03428728000107_20260902_094931.json
│   │   │   ├── risk3_03432310000173_20260902_094932.json
│   │   │   ├── risk3_03468598000136_20260902_094934.json
│   │   │   ├── risk3_03469014000147_20260902_094935.json
│   │   │   ├── risk3_03493431000125_20260902_094935.json
│   │   │   ├── risk3_03499903000157_20260902_094936.json
│   │   │   ├── risk3_03500636000190_20260902_094937.json
│   │   │   ├── risk3_03504139000160_20260902_094938.json
│   │   │   ├── risk3_03505376000146_20260902_094939.json
│   │   │   ├── risk3_03580981000181_20260902_094940.json
│   │   │   ├── risk3_03593705000158_20260902_094940.json
│   │   │   ├── risk3_03632307000101_20260902_094941.json
│   │   │   ├── risk3_03649445000438_20260902_094942.json
│   │   │   ├── risk3_03691432000184_20260902_094943.json
│   │   │   ├── risk3_03714230000100_20260902_094944.json
│   │   │   ├── risk3_03722755000198_20260902_094945.json
│   │   │   ├── risk3_03758625000105_20260902_094945.json
│   │   │   ├── risk3_03761066000192_20260902_094946.json
│   │   │   ├── risk3_03770521001279_20260902_094947.json
│   │   │   ├── risk3_03773419000174_20260902_094948.json
│   │   │   ├── risk3_03780401000108_20260902_094949.json
│   │   │   ├── risk3_03786032000152_20260902_094950.json
│   │   │   ├── risk3_03787133000148_20260902_094950.json
│   │   │   ├── risk3_03802018002068_20260902_094951.json
│   │   │   ├── risk3_03825323000102_20260902_094952.json
│   │   │   ├── risk3_03833260000136_20260902_094953.json
│   │   │   ├── risk3_03839383000184_20260902_094958.json
│   │   │   ├── risk3_03839633000186_20260902_094959.json
│   │   │   ├── risk3_03850692000155_20260902_095000.json
│   │   │   ├── risk3_03852972000100_20260902_095000.json
│   │   │   ├── risk3_03855214000138_20260902_095001.json
│   │   │   ├── risk3_03883369000188_20260902_095002.json
│   │   │   ├── risk3_03913786000126_20260902_095003.json
│   │   │   ├── risk3_03926572000194_20260902_095004.json
│   │   │   ├── risk3_03935003000105_20260902_095005.json
│   │   │   ├── risk3_03959982000131_20260902_095005.json
│   │   │   ├── risk3_03961305000158_20260902_095006.json
│   │   │   ├── risk3_03973903000147_20260902_095007.json
│   │   │   ├── risk3_03979210000161_20260902_095008.json
│   │   │   ├── risk3_03984862000194_20260902_095009.json
│   │   │   ├── risk3_04008938000109_20260902_095010.json
│   │   │   ├── risk3_04011349000180_20260902_095010.json
│   │   │   ├── risk3_04023261000188_20260902_095011.json
│   │   │   ├── risk3_04023387000152_20260902_095012.json
│   │   │   ├── risk3_04037273000161_20260902_095013.json
│   │   │   ├── risk3_04085803000147_20260902_095014.json
│   │   │   ├── risk3_04137003000122_20260902_095015.json
│   │   │   ├── risk3_04143008000168_20260902_095016.json
│   │   │   ├── risk3_04149295000113_20260902_095016.json
│   │   │   ├── risk3_04170860000124_20260902_095017.json
│   │   │   ├── risk3_04176249000103_20260902_095018.json
│   │   │   ├── risk3_04183032000120_20260902_095019.json
│   │   │   ├── risk3_04200198000108_20260902_095020.json
│   │   │   ├── risk3_04200198000299_20260902_095021.json
│   │   │   ├── risk3_04207872000186_20260902_095021.json
│   │   │   ├── risk3_04208296000191_20260902_095022.json
│   │   │   ├── risk3_04270778000171_20260902_095023.json
│   │   │   ├── risk3_04309085000145_20260902_095024.json
│   │   │   ├── risk3_04319855000130_20260902_095025.json
│   │   │   ├── risk3_04326452000119_20260902_095026.json
│   │   │   ├── risk3_04346278000176_20260902_095027.json
│   │   │   ├── risk3_04423567000121_20260902_095028.json
│   │   │   ├── risk3_04429377000111_20260902_095029.json
│   │   │   ├── risk3_04450403000193_20260902_095030.json
│   │   │   ├── risk3_04463344000198_20260902_095031.json
│   │   │   ├── risk3_04475667000100_20260902_095031.json
│   │   │   ├── risk3_04518259000180_20260902_095032.json
│   │   │   ├── risk3_04533831000180_20260902_095033.json
│   │   │   ├── risk3_04557530000196_20260902_095034.json
│   │   │   ├── risk3_04565361000136_20260902_095035.json
│   │   │   ├── risk3_04592014000100_20260902_095036.json
│   │   │   ├── risk3_04602461000195_20260902_095038.json
│   │   │   ├── risk3_04613547000113_20260902_095038.json
│   │   │   ├── risk3_04626426004608_20260902_095039.json
│   │   │   ├── risk3_04630268000168_20260902_095040.json
│   │   │   ├── risk3_04647226000130_20260902_095041.json
│   │   │   ├── risk3_04656253000179_20260902_095042.json
│   │   │   ├── risk3_04694319000115_20260902_095042.json
│   │   │   ├── risk3_04695131000191_20260902_095043.json
│   │   │   ├── risk3_04706606000106_20260902_095044.json
│   │   │   ├── risk3_04708093000164_20260902_095045.json
│   │   │   ├── risk3_04721465000192_20260902_095046.json
│   │   │   ├── risk3_04741986000101_20260902_095047.json
│   │   │   ├── risk3_04753947000124_20260902_095047.json
│   │   │   ├── risk3_04772922000178_20260902_095048.json
│   │   │   ├── risk3_04774215000110_20260902_095049.json
│   │   │   ├── risk3_04817933000127_20260902_095050.json
│   │   │   ├── risk3_04836055000197_20260902_095051.json
│   │   │   ├── risk3_04846140000136_20260902_095051.json
│   │   │   ├── risk3_04854278000187_20260902_095052.json
│   │   │   ├── risk3_04856747000105_20260902_095053.json
│   │   │   ├── risk3_04865359000182_20260902_095054.json
│   │   │   ├── risk3_04877281000116_20260902_095055.json
│   │   │   ├── risk3_04905537000151_20260902_095057.json
│   │   │   ├── risk3_04906823000131_20260902_095057.json
│   │   │   ├── risk3_04908757000139_20260902_095058.json
│   │   │   ├── risk3_04945225000171_20260902_095059.json
│   │   │   ├── risk3_04955577000108_20260902_095100.json
│   │   │   ├── risk3_04973790000142_20260902_095101.json
│   │   │   ├── risk3_04976303000103_20260902_095101.json
│   │   │   ├── risk3_05007043000112_20260902_095102.json
│   │   │   ├── risk3_05029991000159_20260902_095103.json
│   │   │   ├── risk3_05034587000173_20260902_095104.json
│   │   │   ├── risk3_05039806000107_20260902_095105.json
│   │   │   ├── risk3_05065604000210_20260902_095106.json
│   │   │   ├── risk3_05140162000149_20260902_095107.json
│   │   │   ├── risk3_05147464000149_20260902_095107.json
│   │   │   ├── risk3_05150338000143_20260902_095108.json
│   │   │   ├── risk3_05158808000115_20260902_095109.json
│   │   │   ├── risk3_05162775000187_20260902_095110.json
│   │   │   ├── risk3_05206031000117_20260902_095111.json
│   │   │   ├── risk3_05263293000113_20260902_095112.json
│   │   │   ├── risk3_05265768000291_20260902_095113.json
│   │   │   ├── risk3_05288648000129_20260902_095113.json
│   │   │   ├── risk3_05297665000122_20260902_095114.json
│   │   │   ├── risk3_05309161000185_20260902_095115.json
│   │   │   ├── risk3_05311209000190_20260902_095116.json
│   │   │   ├── risk3_05321589000143_20260902_095117.json
│   │   │   ├── risk3_05325158000155_20260902_095118.json
│   │   │   ├── risk3_05350372000161_20260902_095118.json
│   │   │   ├── risk3_05352237000155_20260902_095119.json
│   │   │   ├── risk3_05352393000116_20260902_095120.json
│   │   │   ├── risk3_05355352000183_20260902_095121.json
│   │   │   ├── risk3_05367948000101_20260902_095122.json
│   │   │   ├── risk3_05387332000194_20260902_095123.json
│   │   │   ├── risk3_05408610000142_20260902_095123.json
│   │   │   ├── risk3_05428961000115_20260902_095124.json
│   │   │   ├── risk3_05449127000106_20260902_095125.json
│   │   │   ├── risk3_05509738000100_20260902_095126.json
│   │   │   ├── risk3_05510471000163_20260902_095127.json
│   │   │   ├── risk3_05543197000129_20260902_095128.json
│   │   │   ├── risk3_05545073000263_20260902_095128.json
│   │   │   ├── risk3_05551562000147_20260902_095129.json
│   │   │   ├── risk3_05643764000119_20260902_095130.json
│   │   │   ├── risk3_05671160000186_20260902_095131.json
│   │   │   ├── risk3_05677470000108_20260902_095132.json
│   │   │   ├── risk3_05738907000176_20260902_095133.json
│   │   │   ├── risk3_05748063000144_20260902_095134.json
│   │   │   ├── risk3_05771868000109_20260902_095134.json
│   │   │   ├── risk3_05787792000100_20260902_095135.json
│   │   │   ├── risk3_05789622000164_20260902_095136.json
│   │   │   ├── risk3_05796061000120_20260902_095137.json
│   │   │   ├── risk3_05883919000194_20260902_095138.json
│   │   │   ├── risk3_05915146000261_20260902_095139.json
│   │   │   ├── risk3_05935151000155_20260902_095139.json
│   │   │   ├── risk3_05975865000197_20260902_095140.json
│   │   │   ├── risk3_06010210000147_20260902_095141.json
│   │   │   ├── risk3_06037638000183_20260902_095143.json
│   │   │   ├── risk3_06043809000187_20260902_095144.json
│   │   │   ├── risk3_06064123000172_20260902_095144.json
│   │   │   ├── risk3_06075277000160_20260902_095145.json
│   │   │   ├── risk3_06081827000153_20260902_095146.json
│   │   │   ├── risk3_06094065000120_20260902_095147.json
│   │   │   ├── risk3_06113322000123_20260902_095148.json
│   │   │   ├── risk3_06126316000100_20260902_095149.json
│   │   │   ├── risk3_06134559000190_20260902_095150.json
│   │   │   ├── risk3_06138324000177_20260902_095150.json
│   │   │   ├── risk3_06149288000147_20260902_095151.json
│   │   │   ├── risk3_06151384000120_20260902_095152.json
│   │   │   ├── risk3_06268413000138_20260902_095153.json
│   │   │   ├── risk3_06272575000140_20260902_095154.json
│   │   │   ├── risk3_06272793000184_20260902_095155.json
│   │   │   ├── risk3_06287157000126_20260902_095155.json
│   │   │   ├── risk3_06288733000150_20260902_095156.json
│   │   │   ├── risk3_06293564000146_20260902_095157.json
│   │   │   ├── risk3_06325587000195_20260902_095158.json
│   │   │   ├── risk3_06342880000160_20260902_095159.json
│   │   │   ├── risk3_06346534000150_20260902_095200.json
│   │   │   ├── risk3_06700769000107_20260902_095201.json
│   │   │   ├── risk3_06905926000102_20260902_095202.json
│   │   │   ├── risk3_06922415000107_20260902_095203.json
│   │   │   ├── risk3_06928712000151_20260902_095204.json
│   │   │   ├── risk3_06959872000168_20260902_095205.json
│   │   │   ├── risk3_06968935000142_20260902_095206.json
│   │   │   ├── risk3_06973355000143_20260902_095207.json
│   │   │   ├── risk3_07009769000209_20260902_095207.json
│   │   │   ├── risk3_07042960000163_20260902_095208.json
│   │   │   ├── risk3_07072783000168_20260902_095210.json
│   │   │   ├── risk3_07082088000187_20260902_095211.json
│   │   │   ├── risk3_07086487000116_20260902_095212.json
│   │   │   ├── risk3_07116586000101_20260902_095213.json
│   │   │   ├── risk3_07128323000104_20260902_095214.json
│   │   │   ├── risk3_07142188000151_20260902_095215.json
│   │   │   ├── risk3_07168823000170_20260902_095215.json
│   │   │   ├── risk3_07175725000160_20260902_095217.json
│   │   │   ├── risk3_07177083000138_20260902_095218.json
│   │   │   ├── risk3_07196526000138_20260902_095218.json
│   │   │   ├── risk3_07202226000114_20260902_095219.json
│   │   │   ├── risk3_07210771000152_20260902_095220.json
│   │   │   ├── risk3_07242370000184_20260902_095221.json
│   │   │   ├── risk3_07288763000129_20260902_095222.json
│   │   │   ├── risk3_07316858000109_20260902_095223.json
│   │   │   ├── risk3_07322382000119_20260902_095223.json
│   │   │   ├── risk3_07322382000461_20260902_095224.json
│   │   │   ├── risk3_07323566000101_20260902_095225.json
│   │   │   ├── risk3_07328522000166_20260902_095226.json
│   │   │   ├── risk3_07357797000128_20260902_095227.json
│   │   │   ├── risk3_07358761005632_20260902_095228.json
│   │   │   ├── risk3_07364017000177_20260902_095228.json
│   │   │   ├── risk3_07391922000116_20260902_095229.json
│   │   │   ├── risk3_07404052000172_20260902_095230.json
│   │   │   ├── risk3_07414848000106_20260902_095231.json
│   │   │   ├── risk3_07432397000130_20260902_095232.json
│   │   │   ├── risk3_07442711000165_20260902_095233.json
│   │   │   ├── risk3_07456648000116_20260902_095234.json
│   │   │   ├── risk3_07461763000189_20260902_095235.json
│   │   │   ├── risk3_07474363000108_20260902_095236.json
│   │   │   ├── risk3_07516961000100_20260902_095236.json
│   │   │   ├── risk3_07520949000161_20260902_095237.json
│   │   │   ├── risk3_07546158000100_20260902_095238.json
│   │   │   ├── risk3_07547313000103_20260902_095239.json
│   │   │   ├── risk3_07571746000102_20260902_095240.json
│   │   │   ├── risk3_07594978000178_20260902_095241.json
│   │   │   ├── risk3_07599090000128_20260902_095242.json
│   │   │   ├── risk3_07623836000191_20260902_095243.json
│   │   │   ├── risk3_07626763000191_20260902_095243.json
│   │   │   ├── risk3_07630919000108_20260902_095244.json
│   │   │   ├── risk3_07632665000167_20260902_095245.json
│   │   │   ├── risk3_07646232000160_20260902_095246.json
│   │   │   ├── risk3_07662985000160_20260902_095247.json
│   │   │   ├── risk3_07670111000154_20260902_095248.json
│   │   │   ├── risk3_07675450000123_20260902_095248.json
│   │   │   ├── risk3_07695023000107_20260902_095250.json
│   │   │   ├── risk3_07700052000110_20260902_095251.json
│   │   │   ├── risk3_07705880000140_20260902_095252.json
│   │   │   ├── risk3_07715730000118_20260902_095253.json
│   │   │   ├── risk3_07757548000120_20260902_095254.json
│   │   │   ├── risk3_07764255000170_20260902_095254.json
│   │   │   ├── risk3_07764436000104_20260902_095255.json
│   │   │   ├── risk3_07794616000120_20260902_095256.json
│   │   │   ├── risk3_07804938000103_20260902_095257.json
│   │   │   ├── risk3_07815053000100_20260902_095258.json
│   │   │   ├── risk3_07820488000142_20260902_095259.json
│   │   │   ├── risk3_07827555000150_20260902_095300.json
│   │   │   ├── risk3_07859910000173_20260902_095300.json
│   │   │   ├── risk3_07982576000140_20260902_095301.json
│   │   │   ├── risk3_08029323000110_20260902_095302.json
│   │   │   ├── risk3_08032643000129_20260902_095303.json
│   │   │   ├── risk3_08093504000105_20260902_095304.json
│   │   │   ├── risk3_08149559000190_20260902_095305.json
│   │   │   ├── risk3_08153018000135_20260902_095306.json
│   │   │   ├── risk3_08174968000146_20260902_095306.json
│   │   │   ├── risk3_08211550000161_20260902_095307.json
│   │   │   ├── risk3_08244492000172_20260902_095308.json
│   │   │   ├── risk3_08246483000110_20260902_095309.json
│   │   │   ├── risk3_08306220000150_20260902_095310.json
│   │   │   ├── risk3_08401841000112_20260902_095311.json
│   │   │   ├── risk3_08438586000182_20260902_095312.json
│   │   │   ├── risk3_08446503000105_20260902_095313.json
│   │   │   ├── risk3_08495998000154_20260902_095314.json
│   │   │   ├── risk3_08540795000132_20260902_095315.json
│   │   │   ├── risk3_08540795001104_20260902_095316.json
│   │   │   ├── risk3_08542795000171_20260902_095317.json
│   │   │   ├── risk3_08573833000153_20260902_095319.json
│   │   │   ├── risk3_08578334000159_20260902_095320.json
│   │   │   ├── risk3_08643404000105_20260902_095321.json
│   │   │   ├── risk3_08709009000188_20260902_095321.json
│   │   │   ├── risk3_08719943000180_20260902_095322.json
│   │   │   ├── risk3_08811119000822_20260902_095323.json
│   │   │   ├── risk3_08876164000199_20260902_095324.json
│   │   │   ├── risk3_08893112000120_20260902_095325.json
│   │   │   ├── risk3_08895369000111_20260902_095326.json
│   │   │   ├── risk3_08916434000148_20260902_095326.json
│   │   │   ├── risk3_08935629000305_20260902_095327.json
│   │   │   ├── risk3_08965200000190_20260902_095328.json
│   │   │   ├── risk3_09044272000168_20260902_095329.json
│   │   │   ├── risk3_09088053000180_20260902_095330.json
│   │   │   ├── risk3_09091832000135_20260902_095331.json
│   │   │   ├── risk3_09092458000192_20260902_095331.json
│   │   │   ├── risk3_09149503000106_20260902_095333.json
│   │   │   ├── risk3_09170802000114_20260902_095334.json
│   │   │   ├── risk3_09175059000195_20260902_095335.json
│   │   │   ├── risk3_09257223000103_20260902_095336.json
│   │   │   ├── risk3_09281025000185_20260902_095336.json
│   │   │   ├── risk3_09295194000174_20260902_095337.json
│   │   │   ├── risk3_09375285000110_20260902_095339.json
│   │   │   ├── risk3_09391823000240_20260902_095340.json
│   │   │   ├── risk3_09436149000192_20260902_095341.json
│   │   │   ├── risk3_09454624000153_20260902_095342.json
│   │   │   ├── risk3_09456668000112_20260902_095343.json
│   │   │   ├── risk3_09461639000149_20260902_095343.json
│   │   │   ├── risk3_09467816000102_20260902_095344.json
│   │   │   ├── risk3_09470851000172_20260902_095345.json
│   │   │   ├── risk3_09491921000179_20260902_095346.json
│   │   │   ├── risk3_09495582000107_20260902_095347.json
│   │   │   ├── risk3_09548347000148_20260902_095348.json
│   │   │   ├── risk3_09607810000185_20260902_095348.json
│   │   │   ├── risk3_09967852000127_20260902_095350.json
│   │   │   ├── risk3_10140938000160_20260902_095350.json
│   │   │   ├── risk3_10174877000152_20260902_095351.json
│   │   │   ├── risk3_10207856000196_20260902_095352.json
│   │   │   ├── risk3_10239097000143_20260902_095353.json
│   │   │   ├── risk3_10241516000181_20260902_095354.json
│   │   │   ├── risk3_10254617000197_20260902_095355.json
│   │   │   ├── risk3_10285760000146_20260902_095356.json
│   │   │   ├── risk3_10338369000162_20260902_095357.json
│   │   │   ├── risk3_10356783000102_20260902_095357.json
│   │   │   ├── risk3_10416174000193_20260902_095358.json
│   │   │   ├── risk3_10452113000181_20260902_095359.json
│   │   │   ├── risk3_10466983000100_20260902_095400.json
│   │   │   ├── risk3_10472968000174_20260902_095401.json
│   │   │   ├── risk3_10546614000127_20260902_095402.json
│   │   │   ├── risk3_10614641000190_20260902_095403.json
│   │   │   ├── risk3_10671322000116_20260902_095404.json
│   │   │   ├── risk3_10699948000130_20260902_095405.json
│   │   │   ├── risk3_10740245000109_20260902_095406.json
│   │   │   ├── risk3_10828619000142_20260902_095407.json
│   │   │   ├── risk3_10842044000112_20260902_095408.json
│   │   │   ├── risk3_10902008000105_20260902_095409.json
│   │   │   ├── risk3_10902331000170_20260902_095410.json
│   │   │   ├── risk3_10915021000190_20260902_095411.json
│   │   │   ├── risk3_10931741000140_20260902_095412.json
│   │   │   ├── risk3_11007902000176_20260902_095413.json
│   │   │   ├── risk3_11032345000143_20260902_095414.json
│   │   │   ├── risk3_11041102000171_20260902_095415.json
│   │   │   ├── risk3_11156540000185_20260902_095416.json
│   │   │   ├── risk3_11234162000100_20260902_095416.json
│   │   │   ├── risk3_11279026000137_20260902_095417.json
│   │   │   ├── risk3_11283356000104_20260902_095418.json
│   │   │   ├── risk3_11315117000180_20260902_095419.json
│   │   │   ├── risk3_11322550000224_20260902_095421.json
│   │   │   ├── risk3_11382228000100_20260902_095422.json
│   │   │   ├── risk3_11384227000102_20260902_095422.json
│   │   │   ├── risk3_11386376000100_20260902_095423.json
│   │   │   ├── risk3_11419457000151_20260902_095424.json
│   │   │   ├── risk3_11419911000174_20260902_095425.json
│   │   │   ├── risk3_11517841007957_20260902_095426.json
│   │   │   ├── risk3_11523063000149_20260902_095427.json
│   │   │   ├── risk3_11568948000164_20260902_095428.json
│   │   │   ├── risk3_11586009000142_20260902_095428.json
│   │   │   ├── risk3_11599292000147_20260902_095429.json
│   │   │   ├── risk3_11621915000130_20260902_095430.json
│   │   │   ├── risk3_11659958000105_20260902_095431.json
│   │   │   ├── risk3_11862955000174_20260902_095432.json
│   │   │   ├── risk3_12011542000149_20260902_095433.json
│   │   │   ├── risk3_12027723000163_20260902_095433.json
│   │   │   ├── risk3_12073475000197_20260902_095434.json
│   │   │   ├── risk3_12094479000151_20260902_095435.json
│   │   │   ├── risk3_12130090000114_20260902_095436.json
│   │   │   ├── risk3_12163581000161_20260902_095437.json
│   │   │   ├── risk3_12312945000128_20260902_095438.json
│   │   │   ├── risk3_12320940000147_20260902_095438.json
│   │   │   ├── risk3_12348206000196_20260902_095439.json
│   │   │   ├── risk3_12513940000163_20260902_095440.json
│   │   │   ├── risk3_12543217000127_20260902_095441.json
│   │   │   ├── risk3_12546508000179_20260902_095442.json
│   │   │   ├── risk3_12593013000109_20260902_095443.json
│   │   │   ├── risk3_12659112000138_20260902_095443.json
│   │   │   ├── risk3_12695141000155_20260902_095444.json
│   │   │   ├── risk3_12809025000110_20260902_095445.json
│   │   │   ├── risk3_12884672000510_20260902_095446.json
│   │   │   ├── risk3_12924620000104_20260902_095447.json
│   │   │   ├── risk3_12987729000182_20260902_095447.json
│   │   │   ├── risk3_13061918000192_20260902_095448.json
│   │   │   ├── risk3_13091683000181_20260902_095449.json
│   │   │   ├── risk3_13123801000196_20260902_095450.json
│   │   │   ├── risk3_13176619000101_20260902_095451.json
│   │   │   ├── risk3_13243573000198_20260902_095451.json
│   │   │   ├── risk3_13338734000127_20260902_095452.json
│   │   │   ├── risk3_13374270000104_20260902_095453.json
│   │   │   ├── risk3_13416922000126_20260902_095454.json
│   │   │   ├── risk3_13459301000120_20260902_095455.json
│   │   │   ├── risk3_13547619000162_20260902_095455.json
│   │   │   ├── risk3_13581313000122_20260902_095456.json
│   │   │   ├── risk3_13645518000124_20260902_095457.json
│   │   │   ├── risk3_13700609000115_20260902_095458.json
│   │   │   ├── risk3_13711686000170_20260902_095459.json
│   │   │   ├── risk3_13722308000192_20260902_095500.json
│   │   │   ├── risk3_13844786000175_20260902_095501.json
│   │   │   ├── risk3_13861424000192_20260902_095502.json
│   │   │   ├── risk3_13890438000134_20260902_095503.json
│   │   │   ├── risk3_13897477000163_20260902_095504.json
│   │   │   ├── risk3_13923945000127_20260902_095504.json
│   │   │   ├── risk3_13975154000140_20260902_095505.json
│   │   │   ├── risk3_14011603000101_20260902_095506.json
│   │   │   ├── risk3_14049467000130_20260902_095507.json
│   │   │   ├── risk3_14055501000180_20260902_095508.json
│   │   │   ├── risk3_14073441000128_20260902_095509.json
│   │   │   ├── risk3_14089519000100_20260902_095509.json
│   │   │   ├── risk3_14094415000186_20260902_095510.json
│   │   │   ├── risk3_14171796000150_20260902_095511.json
│   │   │   ├── risk3_14180156000106_20260902_095512.json
│   │   │   ├── risk3_14295008000137_20260902_095513.json
│   │   │   ├── risk3_14475006000120_20260902_095513.json
│   │   │   ├── risk3_14483137000230_20260902_095514.json
│   │   │   ├── risk3_14555633000170_20260902_095515.json
│   │   │   ├── risk3_14609649000119_20260902_095516.json
│   │   │   ├── risk3_14658216000153_20260902_095517.json
│   │   │   ├── risk3_14738147000198_20260902_095518.json
│   │   │   ├── risk3_14738350000164_20260902_095518.json
│   │   │   ├── risk3_14799060000120_20260902_095519.json
│   │   │   ├── risk3_15108924000183_20260902_095520.json
│   │   │   ├── risk3_15163403000129_20260902_095521.json
│   │   │   ├── risk3_15170723000106_20260902_095522.json
│   │   │   ├── risk3_15174398000150_20260902_095522.json
│   │   │   ├── risk3_15186494000118_20260902_095523.json
│   │   │   ├── risk3_15217260000190_20260902_095524.json
│   │   │   ├── risk3_15307114000156_20260902_095525.json
│   │   │   ├── risk3_15330530000175_20260902_095526.json
│   │   │   ├── risk3_15373395000145_20260902_095527.json
│   │   │   ├── risk3_15388514000133_20260902_095527.json
│   │   │   ├── risk3_15458171000136_20260902_095528.json
│   │   │   ├── risk3_15515966000139_20260902_095529.json
│   │   │   ├── risk3_15568388000107_20260902_095530.json
│   │   │   ├── risk3_15623286000139_20260902_095531.json
│   │   │   ├── risk3_15688196000126_20260902_095532.json
│   │   │   ├── risk3_16367850000162_20260902_095532.json
│   │   │   ├── risk3_16404287000155_20260902_095533.json
│   │   │   ├── risk3_16561291000127_20260902_095534.json
│   │   │   ├── risk3_16793501000102_20260902_095535.json
│   │   │   ├── risk3_16804519000162_20260902_095536.json
│   │   │   ├── risk3_16875048000183_20260902_095536.json
│   │   │   ├── risk3_16928294000156_20260902_095537.json
│   │   │   ├── risk3_17069905000110_20260902_095538.json
│   │   │   ├── risk3_17112981000161_20260902_095540.json
│   │   │   ├── risk3_17115437000173_20260902_095541.json
│   │   │   ├── risk3_17176987000100_20260902_095542.json
│   │   │   ├── risk3_17210843000115_20260902_095542.json
│   │   │   ├── risk3_17247679000110_20260902_095543.json
│   │   │   ├── risk3_17313041000130_20260902_095544.json
│   │   │   ├── risk3_17385003000193_20260902_095545.json
│   │   │   ├── risk3_17461715000225_20260902_095546.json
│   │   │   ├── risk3_17465122000156_20260902_095547.json
│   │   │   ├── risk3_17481242000147_20260902_095548.json
│   │   │   ├── risk3_17531314000113_20260902_095549.json
│   │   │   ├── risk3_17555263000160_20260902_095550.json
│   │   │   ├── risk3_17838797000101_20260902_095551.json
│   │   │   ├── risk3_17851152000109_20260902_095551.json
│   │   │   ├── risk3_17858631000149_20260902_095552.json
│   │   │   ├── risk3_18184793000101_20260902_095553.json
│   │   │   ├── risk3_18216718000185_20260902_095554.json
│   │   │   ├── risk3_18384740000134_20260902_095555.json
│   │   │   ├── risk3_18416364000112_20260902_095555.json
│   │   │   ├── risk3_18605172000154_20260902_095556.json
│   │   │   ├── risk3_18748235000121_20260902_095557.json
│   │   │   ├── risk3_18788137000118_20260902_095558.json
│   │   │   ├── risk3_18852832000100_20260902_095559.json
│   │   │   ├── risk3_18856003000197_20260902_095559.json
│   │   │   ├── risk3_18866111000140_20260902_095600.json
│   │   │   ├── risk3_18972990000195_20260902_095601.json
│   │   │   ├── risk3_18983409000130_20260902_095602.json
│   │   │   ├── risk3_19020939000146_20260902_095603.json
│   │   │   ├── risk3_19125927000186_20260902_095604.json
│   │   │   ├── risk3_19170243000104_20260902_095605.json
│   │   │   ├── risk3_19205227000100_20260902_095606.json
│   │   │   ├── risk3_19223945000109_20260902_095606.json
│   │   │   ├── risk3_19267297000184_20260902_095607.json
│   │   │   ├── risk3_19328827000742_20260902_095608.json
│   │   │   ├── risk3_19328827000823_20260902_095609.json
│   │   │   ├── risk3_19445340000154_20260902_095610.json
│   │   │   ├── risk3_19570655000123_20260902_095611.json
│   │   │   ├── risk3_19577977000102_20260902_095612.json
│   │   │   ├── risk3_19629444000119_20260902_095613.json
│   │   │   ├── risk3_19631099000158_20260902_095614.json
│   │   │   ├── risk3_19813045000103_20260902_095615.json
│   │   │   ├── risk3_19868024000195_20260902_095616.json
│   │   │   ├── risk3_19868855000167_20260902_095617.json
│   │   │   ├── risk3_19890579000133_20260902_095617.json
│   │   │   ├── risk3_19925848000150_20260902_095618.json
│   │   │   ├── risk3_19998958000141_20260902_095619.json
│   │   │   ├── risk3_20040441000124_20260902_095620.json
│   │   │   ├── risk3_20088535000173_20260902_095621.json
│   │   │   ├── risk3_20216840000101_20260902_095622.json
│   │   │   ├── risk3_20494564000216_20260902_095623.json
│   │   │   ├── risk3_20500092000186_20260902_095623.json
│   │   │   ├── risk3_20557422000170_20260902_095624.json
│   │   │   ├── risk3_20641255000140_20260902_095625.json
│   │   │   ├── risk3_20835381000136_20260902_095626.json
│   │   │   ├── risk3_20844980000116_20260902_095627.json
│   │   │   ├── risk3_21034389000166_20260902_095628.json
│   │   │   ├── risk3_21069040000160_20260902_095628.json
│   │   │   ├── risk3_21093385000159_20260902_095629.json
│   │   │   ├── risk3_21160480000128_20260902_095630.json
│   │   │   ├── risk3_21169348000349_20260902_095631.json
│   │   │   ├── risk3_21180182000108_20260902_095632.json
│   │   │   ├── risk3_21213298000198_20260902_095632.json
│   │   │   ├── risk3_21411283000134_20260902_095633.json
│   │   │   ├── risk3_21572069000160_20260902_095634.json
│   │   │   ├── risk3_21612448000136_20260902_095635.json
│   │   │   ├── risk3_21812954000179_20260902_095636.json
│   │   │   ├── risk3_21842878000225_20260902_095637.json
│   │   │   ├── risk3_21857228000172_20260902_095637.json
│   │   │   ├── risk3_21908856000130_20260902_095638.json
│   │   │   ├── risk3_21908918000103_20260902_095639.json
│   │   │   ├── risk3_22084882000153_20260902_095640.json
│   │   │   ├── risk3_22109465000118_20260902_095641.json
│   │   │   ├── risk3_22170908000186_20260902_095641.json
│   │   │   ├── risk3_22303462000544_20260902_095642.json
│   │   │   ├── risk3_22350122000140_20260902_095643.json
│   │   │   ├── risk3_22395724000114_20260902_095644.json
│   │   │   ├── risk3_22553164000189_20260902_095645.json
│   │   │   ├── risk3_22664469000168_20260902_095646.json
│   │   │   ├── risk3_22753966000132_20260902_095646.json
│   │   │   ├── risk3_22819418000168_20260902_095647.json
│   │   │   ├── risk3_22996480000125_20260902_095648.json
│   │   │   ├── risk3_23063277000169_20260902_095649.json
│   │   │   ├── risk3_23096269000119_20260902_095650.json
│   │   │   ├── risk3_23253637000195_20260902_095655.json
│   │   │   ├── risk3_23437255000111_20260902_095656.json
│   │   │   ├── risk3_23455342000100_20260902_095656.json
│   │   │   ├── risk3_23704333000288_20260902_095657.json
│   │   │   ├── risk3_23869251000102_20260902_095658.json
│   │   │   ├── risk3_23890953000178_20260902_095659.json
│   │   │   ├── risk3_23892355000138_20260902_095700.json
│   │   │   ├── risk3_24058142000178_20260902_095700.json
│   │   │   ├── risk3_24325696000194_20260902_095701.json
│   │   │   ├── risk3_24332457000161_20260902_095702.json
│   │   │   ├── risk3_24510849000173_20260902_095703.json
│   │   │   ├── risk3_24550050000100_20260902_095704.json
│   │   │   ├── risk3_24632868000172_20260902_095705.json
│   │   │   ├── risk3_24684129000124_20260902_095706.json
│   │   │   ├── risk3_24771203000140_20260902_095706.json
│   │   │   ├── risk3_24797759000105_20260902_095707.json
│   │   │   ├── risk3_25079719000190_20260902_095708.json
│   │   │   ├── risk3_25099255000184_20260902_095710.json
│   │   │   ├── risk3_25369840000157_20260902_095711.json
│   │   │   ├── risk3_25376211000154_20260902_095712.json
│   │   │   ├── risk3_25401457000139_20260902_095713.json
│   │   │   ├── risk3_25982817000133_20260902_095713.json
│   │   │   ├── risk3_26060377000120_20260902_095714.json
│   │   │   ├── risk3_26105453000176_20260902_095715.json
│   │   │   ├── risk3_26222245000157_20260902_095716.json
│   │   │   ├── risk3_26437612000130_20260902_095717.json
│   │   │   ├── risk3_26589893000146_20260902_095718.json
│   │   │   ├── risk3_26608960000122_20260902_095719.json
│   │   │   ├── risk3_26628428000177_20260902_095719.json
│   │   │   ├── risk3_26689080000128_20260902_095720.json
│   │   │   ├── risk3_26711428000136_20260902_095721.json
│   │   │   ├── risk3_26878725000170_20260902_095722.json
│   │   │   ├── risk3_26914969000161_20260902_095723.json
│   │   │   ├── risk3_27133259000167_20260902_095725.json
│   │   │   ├── risk3_27483435000190_20260902_095726.json
│   │   │   ├── risk3_27657485000147_20260902_095727.json
│   │   │   ├── risk3_27796415000250_20260902_095728.json
│   │   │   ├── risk3_27836329000143_20260902_095729.json
│   │   │   ├── risk3_27945263000120_20260902_095730.json
│   │   │   ├── risk3_28060882000108_20260902_095731.json
│   │   │   ├── risk3_28240693000109_20260902_095731.json
│   │   │   ├── risk3_28397998000129_20260902_095732.json
│   │   │   ├── risk3_28461930000161_20260902_095733.json
│   │   │   ├── risk3_28547761000187_20260902_095734.json
│   │   │   ├── risk3_28583371000162_20260902_095735.json
│   │   │   ├── risk3_28672996000605_20260902_095736.json
│   │   │   ├── risk3_28691601000107_20260902_095736.json
│   │   │   ├── risk3_28758086000135_20260902_095737.json
│   │   │   ├── risk3_28835723000120_20260902_095738.json
│   │   │   ├── risk3_28969492000147_20260902_095739.json
│   │   │   ├── risk3_29142202000150_20260902_095740.json
│   │   │   ├── risk3_29170776000131_20260902_095741.json
│   │   │   ├── risk3_29198324000168_20260902_095741.json
│   │   │   ├── risk3_29224131000134_20260902_095742.json
│   │   │   ├── risk3_29244465000170_20260902_095743.json
│   │   │   ├── risk3_29270235000185_20260902_095744.json
│   │   │   ├── risk3_29340729000199_20260902_095745.json
│   │   │   ├── risk3_29527877000117_20260902_095745.json
│   │   │   ├── risk3_29591504000105_20260902_095746.json
│   │   │   ├── risk3_29678871000140_20260902_095747.json
│   │   │   ├── risk3_29752951000107_20260902_095748.json
│   │   │   ├── risk3_29872616000134_20260902_095749.json
│   │   │   ├── risk3_29920394000188_20260902_095750.json
│   │   │   ├── risk3_29953203000184_20260902_095750.json
│   │   │   ├── risk3_29984961000160_20260902_095751.json
│   │   │   ├── risk3_30053915000126_20260902_095752.json
│   │   │   ├── risk3_30058920000121_20260902_095753.json
│   │   │   ├── risk3_30063842000153_20260902_095754.json
│   │   │   ├── risk3_30234798000105_20260902_095755.json
│   │   │   ├── risk3_30248458000125_20260902_095756.json
│   │   │   ├── risk3_30306294000226_20260902_095757.json
│   │   │   ├── risk3_30471204000171_20260902_095757.json
│   │   │   ├── risk3_30559132000119_20260902_095758.json
│   │   │   ├── risk3_30653328000178_20260902_095759.json
│   │   │   ├── risk3_30694272000108_20260902_095800.json
│   │   │   ├── risk3_30712938000103_20260902_095801.json
│   │   │   ├── risk3_30840548000100_20260902_095802.json
│   │   │   ├── risk3_31264770000175_20260902_095802.json
│   │   │   ├── risk3_31635668000139_20260902_095803.json
│   │   │   ├── risk3_31642161000102_20260902_095804.json
│   │   │   ├── risk3_31672016000174_20260902_095805.json
│   │   │   ├── risk3_31702947000330_20260902_095806.json
│   │   │   ├── risk3_31781135000165_20260902_095807.json
│   │   │   ├── risk3_31818954000130_20260902_095808.json
│   │   │   ├── risk3_31835348000122_20260902_095808.json
│   │   │   ├── risk3_32023463000165_20260902_095809.json
│   │   │   ├── risk3_32039151000140_20260902_095810.json
│   │   │   ├── risk3_32135034000180_20260902_095811.json
│   │   │   ├── risk3_32135359000910_20260902_095812.json
│   │   │   ├── risk3_32314495000110_20260902_095813.json
│   │   │   ├── risk3_32367504000130_20260902_095815.json
│   │   │   ├── risk3_32460679000198_20260902_095816.json
│   │   │   ├── risk3_32576121000172_20260902_095817.json
│   │   │   ├── risk3_32593445000119_20260902_095818.json
│   │   │   ├── risk3_32618447000115_20260902_095818.json
│   │   │   ├── risk3_32756560000167_20260902_095819.json
│   │   │   ├── risk3_32957892000452_20260902_095820.json
│   │   │   ├── risk3_33016338000271_20260902_095821.json
│   │   │   ├── risk3_33016338001405_20260902_095822.json
│   │   │   ├── risk3_33051624000197_20260902_095823.json
│   │   │   ├── risk3_33059528000195_20260902_095824.json
│   │   │   ├── risk3_33083466000157_20260902_095825.json
│   │   │   ├── risk3_33401635000150_20260902_095826.json
│   │   │   ├── risk3_33443024000174_20260902_095827.json
│   │   │   ├── risk3_33488348000129_20260902_095827.json
│   │   │   ├── risk3_33611500000119_20260902_095828.json
│   │   │   ├── risk3_33834418000153_20260902_095829.json
│   │   │   ├── risk3_33839828000197_20260902_095830.json
│   │   │   ├── risk3_33856394000133_20260902_095831.json
│   │   │   ├── risk3_33897820000187_20260902_095832.json
│   │   │   ├── risk3_33933760000100_20260902_095833.json
│   │   │   ├── risk3_34108922000139_20260902_095834.json
│   │   │   ├── risk3_34150762000196_20260902_095834.json
│   │   │   ├── risk3_34475373000130_20260902_095835.json
│   │   │   ├── risk3_34497145000161_20260902_095836.json
│   │   │   ├── risk3_34781808000175_20260902_095837.json
│   │   │   ├── risk3_34806971000145_20260902_095839.json
│   │   │   ├── risk3_34847870000112_20260902_095842.json
│   │   │   ├── risk3_35306327000170_20260902_095843.json
│   │   │   ├── risk3_35322362000183_20260902_095844.json
│   │   │   ├── risk3_35357719000169_20260902_095845.json
│   │   │   ├── risk3_35357729000102_20260902_095846.json
│   │   │   ├── risk3_35360212000164_20260902_095847.json
│   │   │   ├── risk3_35382136000198_20260902_095847.json
│   │   │   ├── risk3_35416995000150_20260902_095848.json
│   │   │   ├── risk3_35540155000103_20260902_095850.json
│   │   │   ├── risk3_35540155000103_20260902_134321.json
│   │   │   ├── risk3_35540155000103_20260902_142412.json
│   │   │   ├── risk3_35540155000103_20260902_150913.json
│   │   │   ├── risk3_35540155000103_20260902_151942.json
│   │   │   ├── risk3_35540155000103_20260902_162052.json
│   │   │   ├── risk3_35540155000103_20260902_163210.json
│   │   │   ├── risk3_35540155000103_20260903_114531.json
│   │   │   ├── risk3_35540155000103_20260903_130122.json
│   │   │   ├── risk3_35540155000103_20260903_152547.json
│   │   │   ├── risk3_35540155000103_20260904_101549.json
│   │   │   ├── risk3_35540155000103_20260904_111245.json
│   │   │   ├── risk3_35540155000103_20260904_113818.json
│   │   │   ├── risk3_35540155000103_20260904_134737.json
│   │   │   ├── risk3_35540155000103_20260904_140640.json
│   │   │   ├── risk3_35540155000103_20260909_134829.json
│   │   │   ├── risk3_35540155000103_20260909_150225.json
│   │   │   ├── risk3_35540155000103_20260909_152142.json
│   │   │   ├── risk3_35540155000103_20260909_163510.json
│   │   │   ├── risk3_35540155000103_20260909_171552.json
│   │   │   ├── risk3_35540155000103_20260910_104934.json
│   │   │   ├── risk3_35540155000103_20260910_110742.json
│   │   │   ├── risk3_35540155000103_20260910_112309.json
│   │   │   ├── risk3_35540155000103_20260910_154517.json
│   │   │   ├── risk3_35691397000190_20260902_095851.json
│   │   │   ├── risk3_35749859000182_20260902_095852.json
│   │   │   ├── risk3_35823536000191_20260902_095854.json
│   │   │   ├── risk3_35823538000180_20260902_095854.json
│   │   │   ├── risk3_35823577000188_20260902_095855.json
│   │   │   ├── risk3_35824347000133_20260902_095856.json
│   │   │   ├── risk3_35835571000120_20260902_095857.json
│   │   │   ├── risk3_35835582000100_20260902_095858.json
│   │   │   ├── risk3_35859013000103_20260902_095859.json
│   │   │   ├── risk3_35865623000101_20260902_095900.json
│   │   │   ├── risk3_35865638000170_20260902_095901.json
│   │   │   ├── risk3_35911730000129_20260902_095904.json
│   │   │   ├── risk3_35911733000162_20260902_095905.json
│   │   │   ├── risk3_35912298000190_20260902_095906.json
│   │   │   ├── risk3_36012033000107_20260902_095907.json
│   │   │   ├── risk3_36159672000191_20260902_095908.json
│   │   │   ├── risk3_36205095000127_20260902_095909.json
│   │   │   ├── risk3_36932917000171_20260902_095910.json
│   │   │   ├── risk3_37145968000116_20260902_095911.json
│   │   │   ├── risk3_37275625000419_20260902_095911.json
│   │   │   ├── risk3_37538262000114_20260902_095915.json
│   │   │   ├── risk3_37543498000149_20260902_095915.json
│   │   │   ├── risk3_38908778000176_20260902_095916.json
│   │   │   ├── risk3_39266459000177_20260902_095917.json
│   │   │   ├── risk3_39335973000206_20260902_095918.json
│   │   │   ├── risk3_39372527000182_20260902_095919.json
│   │   │   ├── risk3_39553144000100_20260902_095920.json
│   │   │   ├── risk3_39630440000168_20260902_095920.json
│   │   │   ├── risk3_39657225000150_20260902_095921.json
│   │   │   ├── risk3_39702802000189_20260902_095922.json
│   │   │   ├── risk3_39702815000158_20260902_095923.json
│   │   │   ├── risk3_39702823000102_20260902_095924.json
│   │   │   ├── risk3_39702834000184_20260902_095924.json
│   │   │   ├── risk3_40006524000104_20260902_095927.json
│   │   │   ├── risk3_40009403000116_20260902_095928.json
│   │   │   ├── risk3_40100543000103_20260902_095929.json
│   │   │   ├── risk3_40212058000113_20260902_095930.json
│   │   │   ├── risk3_40283901000152_20260902_095931.json
│   │   │   ├── risk3_40382949000118_20260902_095932.json
│   │   │   ├── risk3_40623898000179_20260902_095933.json
│   │   │   ├── risk3_40692476000155_20260902_095933.json
│   │   │   ├── risk3_40727874000160_20260902_095934.json
│   │   │   ├── risk3_40797554000186_20260902_095935.json
│   │   │   ├── risk3_41324703000152_20260902_095936.json
│   │   │   ├── risk3_41638308000144_20260902_095937.json
│   │   │   ├── risk3_41684120000132_20260902_095937.json
│   │   │   ├── risk3_42008546000139_20260902_095938.json
│   │   │   ├── risk3_42066811000135_20260902_095939.json
│   │   │   ├── risk3_42150391000170_20260902_095940.json
│   │   │   ├── risk3_42355428000105_20260902_095941.json
│   │   │   ├── risk3_42566752000164_20260902_095942.json
│   │   │   ├── risk3_42599019000146_20260902_095943.json
│   │   │   ├── risk3_42599019000308_20260902_095943.json
│   │   │   ├── risk3_42632288000167_20260902_095944.json
│   │   │   ├── risk3_43248129000126_20260902_095945.json
│   │   │   ├── risk3_43308969000137_20260902_095946.json
│   │   │   ├── risk3_43443043000154_20260902_095947.json
│   │   │   ├── risk3_43559079000106_20260902_095948.json
│   │   │   ├── risk3_43594977000197_20260902_095949.json
│   │   │   ├── risk3_43672716000148_20260902_095949.json
│   │   │   ├── risk3_44003911000148_20260902_095950.json
│   │   │   ├── risk3_44010502000179_20260902_095951.json
│   │   │   ├── risk3_44145845000140_20260902_095952.json
│   │   │   ├── risk3_44355306000136_20260902_095953.json
│   │   │   ├── risk3_44701688000102_20260902_095954.json
│   │   │   ├── risk3_44944668000162_20260902_095954.json
│   │   │   ├── risk3_45321225000269_20260902_095955.json
│   │   │   ├── risk3_45365541000151_20260902_095956.json
│   │   │   ├── risk3_45365558000613_20260902_095957.json
│   │   │   ├── risk3_45931904000179_20260902_095958.json
│   │   │   ├── risk3_46082624000104_20260902_095959.json
│   │   │   ├── risk3_46241741000165_20260902_100000.json
│   │   │   ├── risk3_46494301000110_20260902_100001.json
│   │   │   ├── risk3_46766812000143_20260902_100002.json
│   │   │   ├── risk3_46986451000140_20260902_100002.json
│   │   │   ├── risk3_47034509000119_20260902_100003.json
│   │   │   ├── risk3_47055959000198_20260902_100004.json
│   │   │   ├── risk3_47155252000153_20260902_100013.json
│   │   │   ├── risk3_47187794000108_20260902_100014.json
│   │   │   ├── risk3_47488077000116_20260902_100017.json
│   │   │   ├── risk3_47634450000108_20260902_100017.json
│   │   │   ├── risk3_47673906000130_20260902_100018.json
│   │   │   ├── risk3_47865800000210_20260902_100019.json
│   │   │   ├── risk3_47866165000104_20260902_100020.json
│   │   │   ├── risk3_47938840000163_20260902_100021.json
│   │   │   ├── risk3_48563988000123_20260902_100022.json
│   │   │   ├── risk3_48725956000187_20260902_100023.json
│   │   │   ├── risk3_49021009000178_20260902_100023.json
│   │   │   ├── risk3_49392982000101_20260902_100024.json
│   │   │   ├── risk3_49396591000157_20260902_100025.json
│   │   │   ├── risk3_49502032000184_20260902_100026.json
│   │   │   ├── risk3_49729718000102_20260902_100027.json
│   │   │   ├── risk3_49884937000166_20260902_100028.json
│   │   │   ├── risk3_50359850000159_20260902_100029.json
│   │   │   ├── risk3_50475875000118_20260902_100029.json
│   │   │   ├── risk3_50647214000122_20260902_100030.json
│   │   │   ├── risk3_51093193000456_20260902_100031.json
│   │   │   ├── risk3_51399400000314_20260902_100032.json
│   │   │   ├── risk3_51482776000126_20260902_100033.json
│   │   │   ├── risk3_51735503000146_20260902_100034.json
│   │   │   ├── risk3_51775690000191_20260902_100035.json
│   │   │   ├── risk3_51784262000125_20260902_100036.json
│   │   │   ├── risk3_52044676000180_20260902_100036.json
│   │   │   ├── risk3_52123916000132_20260902_100037.json
│   │   │   ├── risk3_52123916000213_20260902_100038.json
│   │   │   ├── risk3_52123916001023_20260902_100039.json
│   │   │   ├── risk3_52311289000163_20260902_100040.json
│   │   │   ├── risk3_53012414000105_20260902_100041.json
│   │   │   ├── risk3_53054965000123_20260902_100042.json
│   │   │   ├── risk3_53056853000101_20260902_100042.json
│   │   │   ├── risk3_53266498000103_20260902_100043.json
│   │   │   ├── risk3_53350047000141_20260902_100044.json
│   │   │   ├── risk3_53804305000112_20260902_100045.json
│   │   │   ├── risk3_53910899000146_20260902_100047.json
│   │   │   ├── risk3_53918116000170_20260902_100047.json
│   │   │   ├── risk3_54218054000157_20260902_100048.json
│   │   │   ├── risk3_54406566000147_20260902_100049.json
│   │   │   ├── risk3_55257059000151_20260902_100050.json
│   │   │   ├── risk3_55685369000177_20260902_100051.json
│   │   │   ├── risk3_55773964000164_20260902_100052.json
│   │   │   ├── risk3_55973762000328_20260902_100053.json
│   │   │   ├── risk3_55979736000145_20260902_100054.json
│   │   │   ├── risk3_55983670000167_20260902_100055.json
│   │   │   ├── risk3_55999932000181_20260902_100056.json
│   │   │   ├── risk3_56139066000626_20260902_100056.json
│   │   │   ├── risk3_56720287000189_20260902_100057.json
│   │   │   ├── risk3_57010480000431_20260902_100058.json
│   │   │   ├── risk3_57107609000343_20260902_100059.json
│   │   │   ├── risk3_57227134000167_20260902_100100.json
│   │   │   ├── risk3_57417453000135_20260902_100101.json
│   │   │   ├── risk3_57879827000304_20260902_100102.json
│   │   │   ├── risk3_58059643000190_20260902_100103.json
│   │   │   ├── risk3_58275042000115_20260902_100104.json
│   │   │   ├── risk3_59247502000164_20260902_100105.json
│   │   │   ├── risk3_59650366000400_20260902_100106.json
│   │   │   ├── risk3_59723874000110_20260902_100107.json
│   │   │   ├── risk3_59762831000143_20260902_100108.json
│   │   │   ├── risk3_59895385000145_20260902_100109.json
│   │   │   ├── risk3_60177862000116_20260902_100110.json
│   │   │   ├── risk3_60211893000146_20260902_100111.json
│   │   │   ├── risk3_60619202000148_20260902_100112.json
│   │   │   ├── risk3_60820198000262_20260902_100113.json
│   │   │   ├── risk3_60860277000116_20260902_100114.json
│   │   │   ├── risk3_60872306016244_20260902_100115.json
│   │   │   ├── risk3_60879848000164_20260902_100116.json
│   │   │   ├── risk3_60882313000142_20260902_100117.json
│   │   │   ├── risk3_61036141000310_20260902_100118.json
│   │   │   ├── risk3_61067930000319_20260902_100119.json
│   │   │   ├── risk3_61082988000170_20260902_100120.json
│   │   │   ├── risk3_61139192000459_20260902_100121.json
│   │   │   ├── risk3_61144150000678_20260902_100122.json
│   │   │   ├── risk3_61246245000198_20260902_100123.json
│   │   │   ├── risk3_61310256000190_20260902_100124.json
│   │   │   ├── risk3_61451027000195_20260902_100125.json
│   │   │   ├── risk3_61479002000108_20260902_100126.json
│   │   │   ├── risk3_61526398000199_20260902_100127.json
│   │   │   ├── risk3_61528030000160_20260902_100127.json
│   │   │   ├── risk3_61585865000151_20260902_100128.json
│   │   │   ├── risk3_61597407000132_20260902_100129.json
│   │   │   ├── risk3_61728804000104_20260902_100135.json
│   │   │   ├── risk3_62014352000153_20260902_100136.json
│   │   │   ├── risk3_62125836000170_20260902_100137.json
│   │   │   ├── risk3_62440235000151_20260902_100138.json
│   │   │   ├── risk3_62473004000144_20260902_100139.json
│   │   │   ├── risk3_62695036000194_20260902_100140.json
│   │   │   ├── risk3_62695036005404_20260902_100141.json
│   │   │   ├── risk3_62757224000108_20260902_100142.json
│   │   │   ├── risk3_62801576000105_20260902_100142.json
│   │   │   ├── risk3_62955505006874_20260902_100143.json
│   │   │   ├── risk3_62979232000190_20260902_100144.json
│   │   │   ├── risk3_62988365000123_20260902_100145.json
│   │   │   ├── risk3_64119865000154_20260902_100146.json
│   │   │   ├── risk3_64812373000140_20260902_100147.json
│   │   │   ├── risk3_66693326000150_20260902_100149.json
│   │   │   ├── risk3_66830332000101_20260902_100150.json
│   │   │   ├── risk3_66979659000140_20260902_100150.json
│   │   │   ├── risk3_67051136000363_20260902_100152.json
│   │   │   ├── risk3_67185694000150_20260902_100153.json
│   │   │   ├── risk3_67290858000109_20260902_100153.json
│   │   │   ├── risk3_67969964000113_20260902_100154.json
│   │   │   ├── risk3_68776277000144_20260902_100155.json
│   │   │   ├── risk3_71320915000122_20260902_100156.json
│   │   │   ├── risk3_71322150000160_20260902_100157.json
│   │   │   ├── risk3_72147440000187_20260902_100158.json
│   │   │   ├── risk3_72202773000161_20260902_100159.json
│   │   │   ├── risk3_72366818000133_20260902_100200.json
│   │   │   ├── risk3_72393002000107_20260902_100200.json
│   │   │   ├── risk3_72459373000136_20260902_100201.json
│   │   │   ├── risk3_72909146000165_20260902_100202.json
│   │   │   ├── risk3_73056731000122_20260902_100203.json
│   │   │   ├── risk3_73113367000195_20260902_100204.json
│   │   │   ├── risk3_73217028000159_20260902_100205.json
│   │   │   ├── risk3_73262826000100_20260902_100206.json
│   │   │   ├── risk3_73338824000140_20260902_100207.json
│   │   │   ├── risk3_73379380000190_20260902_100208.json
│   │   │   ├── risk3_73586976000161_20260902_100209.json
│   │   │   ├── risk3_73847782000172_20260902_100210.json
│   │   │   ├── risk3_73954489000104_20260902_100211.json
│   │   │   ├── risk3_73973059000130_20260902_100212.json
│   │   │   ├── risk3_74068552000178_20260902_100213.json
│   │   │   ├── risk3_74175159000183_20260902_100214.json
│   │   │   ├── risk3_74526278000133_20260902_100215.json
│   │   │   ├── risk3_74531997000142_20260902_100216.json
│   │   │   ├── risk3_74657784000161_20260902_100217.json
│   │   │   ├── risk3_75034645000144_20260902_100218.json
│   │   │   ├── risk3_75045591000112_20260902_100219.json
│   │   │   ├── risk3_75047498000147_20260902_100220.json
│   │   │   ├── risk3_75048165000132_20260902_100221.json
│   │   │   ├── risk3_75051458000179_20260902_100222.json
│   │   │   ├── risk3_75084871000130_20260902_100223.json
│   │   │   ├── risk3_75205831000107_20260902_100224.json
│   │   │   ├── risk3_75221028000158_20260902_100224.json
│   │   │   ├── risk3_75222224000147_20260902_100225.json
│   │   │   ├── risk3_75227801000193_20260902_100227.json
│   │   │   ├── risk3_75263921001037_20260902_100228.json
│   │   │   ├── risk3_75272013000119_20260902_100229.json
│   │   │   ├── risk3_75294801000106_20260902_100230.json
│   │   │   ├── risk3_75364455000195_20260902_100231.json
│   │   │   ├── risk3_75483040000211_20260902_100232.json
│   │   │   ├── risk3_75517151000110_20260902_100233.json
│   │   │   ├── risk3_75556431000219_20260902_100233.json
│   │   │   ├── risk3_75556431000561_20260902_100234.json
│   │   │   ├── risk3_75584193000174_20260902_100235.json
│   │   │   ├── risk3_75655720000194_20260902_100236.json
│   │   │   ├── risk3_75674424000130_20260902_100237.json
│   │   │   ├── risk3_75723056000173_20260902_100238.json
│   │   │   ├── risk3_75801936000110_20260902_100239.json
│   │   │   ├── risk3_75864728000160_20260902_100240.json
│   │   │   ├── risk3_75875773000110_20260902_100241.json
│   │   │   ├── risk3_75904383000121_20260902_100242.json
│   │   │   ├── risk3_75915975000149_20260902_100242.json
│   │   │   ├── risk3_75962886000315_20260902_100243.json
│   │   │   ├── risk3_75962886000900_20260902_100244.json
│   │   │   ├── risk3_76004209000195_20260902_100245.json
│   │   │   ├── risk3_76013440000145_20260902_100246.json
│   │   │   ├── risk3_76047638000140_20260902_100247.json
│   │   │   ├── risk3_76071950000179_20260902_100248.json
│   │   │   ├── risk3_76089523000118_20260902_100249.json
│   │   │   ├── risk3_76091768000180_20260902_100250.json
│   │   │   ├── risk3_76097989000165_20260902_100251.json
│   │   │   ├── risk3_76098219000137_20260902_100251.json
│   │   │   ├── risk3_76105436000107_20260902_100253.json
│   │   │   ├── risk3_76109594000135_20260902_100255.json
│   │   │   ├── risk3_76176643000152_20260902_100256.json
│   │   │   ├── risk3_76214022000116_20260902_100257.json
│   │   │   ├── risk3_76255926000190_20260902_100258.json
│   │   │   ├── risk3_76260017000140_20260902_100259.json
│   │   │   ├── risk3_76291251000134_20260902_100300.json
│   │   │   ├── risk3_76396159000139_20260902_100301.json
│   │   │   ├── risk3_76484013000145_20260902_100301.json
│   │   │   ├── risk3_76491950000128_20260902_100302.json
│   │   │   ├── risk3_76492065000163_20260902_100303.json
│   │   │   ├── risk3_76492701000157_20260902_100304.json
│   │   │   ├── risk3_76495779000125_20260902_100305.json
│   │   │   ├── risk3_76498179000110_20260902_100306.json
│   │   │   ├── risk3_76518356000183_20260902_100307.json
│   │   │   ├── risk3_76527951000509_20260902_100308.json
│   │   │   ├── risk3_76545011000119_20260902_100309.json
│   │   │   ├── risk3_76554559000125_20260902_100310.json
│   │   │   ├── risk3_76561406000105_20260902_100311.json
│   │   │   ├── risk3_76564624000101_20260902_100312.json
│   │   │   ├── risk3_76657030000137_20260902_100312.json
│   │   │   ├── risk3_76678697000116_20260902_100313.json
│   │   │   ├── risk3_76681550000185_20260902_100314.json
│   │   │   ├── risk3_76695709000110_20260902_100315.json
│   │   │   ├── risk3_76695923000177_20260902_100316.json
│   │   │   ├── risk3_76743012000178_20260902_100317.json
│   │   │   ├── risk3_76745850000180_20260902_100318.json
│   │   │   ├── risk3_76848506000117_20260902_100319.json
│   │   │   ├── risk3_76857747000122_20260902_100320.json
│   │   │   ├── risk3_76868678000152_20260902_100321.json
│   │   │   ├── risk3_76879295000180_20260902_100322.json
│   │   │   ├── risk3_76881093000172_20260902_100323.json
│   │   │   ├── risk3_76888767000160_20260902_100324.json
│   │   │   ├── risk3_76900463000171_20260902_100325.json
│   │   │   ├── risk3_76902204000180_20260902_100326.json
│   │   │   ├── risk3_76915123000114_20260902_100326.json
│   │   │   ├── risk3_76929660000113_20260902_100327.json
│   │   │   ├── risk3_76947126000130_20260902_100328.json
│   │   │   ├── risk3_77044618000188_20260902_100329.json
│   │   │   ├── risk3_77116770000129_20260902_100330.json
│   │   │   ├── risk3_77152338000193_20260902_100331.json
│   │   │   ├── risk3_77163749000184_20260902_100332.json
│   │   │   ├── risk3_77172161000197_20260902_100333.json
│   │   │   ├── risk3_77172161000510_20260902_100334.json
│   │   │   ├── risk3_77172161000600_20260902_100335.json
│   │   │   ├── risk3_77215606000179_20260902_100335.json
│   │   │   ├── risk3_77307387000158_20260902_100336.json
│   │   │   ├── risk3_77366664000101_20260902_100337.json
│   │   │   ├── risk3_77381259000154_20260902_100338.json
│   │   │   ├── risk3_77388874000192_20260902_100339.json
│   │   │   ├── risk3_77396810000133_20260902_100340.json
│   │   │   ├── risk3_77424992000109_20260902_100341.json
│   │   │   ├── risk3_77595395004487_20260902_100342.json
│   │   │   ├── risk3_77595395005106_20260902_100343.json
│   │   │   ├── risk3_77606911000191_20260902_100344.json
│   │   │   ├── risk3_77716249000122_20260902_100344.json
│   │   │   ├── risk3_77718815000135_20260902_100345.json
│   │   │   ├── risk3_77728988000134_20260902_100346.json
│   │   │   ├── risk3_77752038000226_20260902_100347.json
│   │   │   ├── risk3_77758324000118_20260902_100348.json
│   │   │   ├── risk3_77768943000436_20260902_100349.json
│   │   │   ├── risk3_77781706000243_20260902_100350.json
│   │   │   ├── risk3_77799542000109_20260902_100351.json
│   │   │   ├── risk3_77804599000140_20260902_100352.json
│   │   │   ├── risk3_77837979000181_20260902_100353.json
│   │   │   ├── risk3_77837979001404_20260902_100353.json
│   │   │   ├── risk3_77850568000126_20260902_100354.json
│   │   │   ├── risk3_77867984000137_20260902_100355.json
│   │   │   ├── risk3_77883189000132_20260902_100356.json
│   │   │   ├── risk3_77912053000103_20260902_100357.json
│   │   │   ├── risk3_77917680005104_20260902_100358.json
│   │   │   ├── risk3_77948750000114_20260902_100359.json
│   │   │   ├── risk3_77968980000145_20260902_100359.json
│   │   │   ├── risk3_77975654000165_20260902_100400.json
│   │   │   ├── risk3_78016003000100_20260902_100401.json
│   │   │   ├── risk3_78095023000114_20260902_100402.json
│   │   │   ├── risk3_78116670000165_20260902_100403.json
│   │   │   ├── risk3_78141926000194_20260902_100403.json
│   │   │   ├── risk3_78147105001641_20260902_100404.json
│   │   │   ├── risk3_78156247000199_20260902_100405.json
│   │   │   ├── risk3_78160934000188_20260902_100406.json
│   │   │   ├── risk3_78232485000136_20260902_100407.json
│   │   │   ├── risk3_78282084000190_20260902_100408.json
│   │   │   ├── risk3_78296027000160_20260902_100408.json
│   │   │   ├── risk3_78373305000136_20260902_100409.json
│   │   │   ├── risk3_78567328000181_20260902_100410.json
│   │   │   ├── risk3_78588431000108_20260902_100411.json
│   │   │   ├── risk3_78594926000140_20260902_100412.json
│   │   │   ├── risk3_78624202000100_20260902_100413.json
│   │   │   ├── risk3_78643319000122_20260902_100413.json
│   │   │   ├── risk3_78701232000164_20260902_100414.json
│   │   │   ├── risk3_78712288000114_20260902_100415.json
│   │   │   ├── risk3_78724135000197_20260902_100416.json
│   │   │   ├── risk3_78897600000191_20260902_100417.json
│   │   │   ├── risk3_78897600000272_20260902_100417.json
│   │   │   ├── risk3_78943321000117_20260902_100418.json
│   │   │   ├── risk3_78956968000183_20260902_100419.json
│   │   │   ├── risk3_78956968001589_20260902_100420.json
│   │   │   ├── risk3_78956968001740_20260902_100421.json
│   │   │   ├── risk3_78969466000197_20260902_100422.json
│   │   │   ├── risk3_79077343000104_20260902_100423.json
│   │   │   ├── risk3_79085221000160_20260902_100423.json
│   │   │   ├── risk3_79114450000165_20260902_100424.json
│   │   │   ├── risk3_79142139000120_20260902_100425.json
│   │   │   ├── risk3_79264628000154_20260902_100426.json
│   │   │   ├── risk3_79386678000104_20260902_100427.json
│   │   │   ├── risk3_79390530000305_20260902_100428.json
│   │   │   ├── risk3_79435020000145_20260902_100428.json
│   │   │   ├── risk3_79458485000111_20260902_100429.json
│   │   │   ├── risk3_79571659000158_20260902_100430.json
│   │   │   ├── risk3_79599411000103_20260902_100431.json
│   │   │   ├── risk3_79613030000123_20260902_100432.json
│   │   │   ├── risk3_79704961000137_20260902_100433.json
│   │   │   ├── risk3_79763884000196_20260902_100433.json
│   │   │   ├── risk3_79846341000132_20260902_100434.json
│   │   │   ├── risk3_79863569000130_20260902_100435.json
│   │   │   ├── risk3_79863569005876_20260902_100436.json
│   │   │   ├── risk3_79875183000149_20260902_100437.json
│   │   │   ├── risk3_79939450000102_20260902_100437.json
│   │   │   ├── risk3_80020761000144_20260902_100439.json
│   │   │   ├── risk3_80028194000172_20260902_100440.json
│   │   │   ├── risk3_80213705000126_20260902_100440.json
│   │   │   ├── risk3_80215213000170_20260902_100441.json
│   │   │   ├── risk3_80223324000128_20260902_100442.json
│   │   │   ├── risk3_80232952000170_20260902_100443.json
│   │   │   ├── risk3_80233380000143_20260902_100445.json
│   │   │   ├── risk3_80255060000194_20260902_100445.json
│   │   │   ├── risk3_80337306000177_20260902_100446.json
│   │   │   ├── risk3_80339427000158_20260902_100447.json
│   │   │   ├── risk3_80349020000101_20260902_100448.json
│   │   │   ├── risk3_80358401000157_20260902_100449.json
│   │   │   ├── risk3_80418205000120_20260902_100450.json
│   │   │   ├── risk3_80474042000101_20260902_100450.json
│   │   │   ├── risk3_80513021000140_20260902_100451.json
│   │   │   ├── risk3_80524051000151_20260902_100452.json
│   │   │   ├── risk3_80565161000161_20260902_100453.json
│   │   │   ├── risk3_80605298000100_20260902_100454.json
│   │   │   ├── risk3_80646755000105_20260902_100455.json
│   │   │   ├── risk3_80813710000170_20260902_100455.json
│   │   │   ├── risk3_80840861000117_20260902_100456.json
│   │   │   ├── risk3_80851439000167_20260902_100457.json
│   │   │   ├── risk3_80929532000147_20260902_100458.json
│   │   │   ├── risk3_81174138000109_20260902_100459.json
│   │   │   ├── risk3_81229932000102_20260902_100500.json
│   │   │   ├── risk3_81270548000153_20260902_100500.json
│   │   │   ├── risk3_81433765000117_20260902_100501.json
│   │   │   ├── risk3_81482895000140_20260902_100502.json
│   │   │   ├── risk3_81599359000129_20260902_100503.json
│   │   │   ├── risk3_81611931000128_20260902_100504.json
│   │   │   ├── risk3_81616807000155_20260902_100505.json
│   │   │   ├── risk3_81642308000213_20260902_100506.json
│   │   │   ├── risk3_81662462000176_20260902_100507.json
│   │   │   ├── risk3_81671125000145_20260902_100508.json
│   │   │   ├── risk3_81672099000170_20260902_100509.json
│   │   │   ├── risk3_81716219000193_20260902_100510.json
│   │   │   ├── risk3_81760159000106_20260902_100511.json
│   │   │   ├── risk3_82036641000594_20260902_100512.json
│   │   │   ├── risk3_82052788000144_20260902_100513.json
│   │   │   ├── risk3_82056185000110_20260902_100514.json
│   │   │   ├── risk3_82130956000172_20260902_100515.json
│   │   │   ├── risk3_82270281000167_20260902_100516.json
│   │   │   ├── risk3_82292053000198_20260902_100517.json
│   │   │   ├── risk3_82295817000107_20260902_100518.json
│   │   │   ├── risk3_82310046000171_20260902_100519.json
│   │   │   ├── risk3_82368028000140_20260902_100520.json
│   │   │   ├── risk3_82370743000118_20260902_100520.json
│   │   │   ├── risk3_82381815000122_20260902_100521.json
│   │   │   ├── risk3_82381815000807_20260902_100522.json
│   │   │   ├── risk3_82382458000117_20260902_100523.json
│   │   │   ├── risk3_82423310000183_20260902_100524.json
│   │   │   ├── risk3_82589540000117_20260902_100525.json
│   │   │   ├── risk3_82598863000177_20260902_100526.json
│   │   │   ├── risk3_82658840000100_20260902_100527.json
│   │   │   ├── risk3_82666330000185_20260902_100528.json
│   │   │   ├── risk3_82757907000164_20260902_100528.json
│   │   │   ├── risk3_82984287000104_20260902_100529.json
│   │   │   ├── risk3_83096123000103_20260902_100530.json
│   │   │   ├── risk3_83175661000185_20260902_100531.json
│   │   │   ├── risk3_83305235000119_20260902_100532.json
│   │   │   ├── risk3_83305235023402_20260902_100532.json
│   │   │   ├── risk3_83310441000117_20260902_100533.json
│   │   │   ├── risk3_83631051000149_20260902_100534.json
│   │   │   ├── risk3_83647990000181_20260902_100535.json
│   │   │   ├── risk3_83731927000129_20260902_100536.json
│   │   │   ├── risk3_83781641000158_20260902_100537.json
│   │   │   ├── risk3_83816694000167_20260902_100538.json
│   │   │   ├── risk3_84229889000173_20260902_100539.json
│   │   │   ├── risk3_84298926000103_20260902_100540.json
│   │   │   ├── risk3_84831478000153_20260902_100541.json
│   │   │   ├── risk3_84894138000171_20260902_100541.json
│   │   │   ├── risk3_84897313000184_20260902_100542.json
│   │   │   ├── risk3_84900091000101_20260902_100543.json
│   │   │   ├── risk3_84963370000114_20260902_100544.json
│   │   │   ├── risk3_85285963000131_20260902_100545.json
│   │   │   ├── risk3_85307098000187_20260902_100546.json
│   │   │   ├── risk3_85462471000174_20260902_100547.json
│   │   │   ├── risk3_85462927000104_20260902_100547.json
│   │   │   ├── risk3_85494201000145_20260902_100548.json
│   │   │   ├── risk3_86046414000177_20260902_100549.json
│   │   │   ├── risk3_86046448000161_20260902_100550.json
│   │   │   ├── risk3_86375912000163_20260902_100551.json
│   │   │   ├── risk3_86378189000176_20260902_100552.json
│   │   │   ├── risk3_86378866000156_20260902_100553.json
│   │   │   ├── risk3_87248522000195_20260902_100554.json
│   │   │   ├── risk3_87442430000141_20260902_100555.json
│   │   │   ├── risk3_87755799000104_20260902_100556.json
│   │   │   ├── risk3_88065321000115_20260902_100556.json
│   │   │   ├── risk3_88112313000182_20260902_100557.json
│   │   │   ├── risk3_88371075000120_20260902_100558.json
│   │   │   ├── risk3_88418686000186_20260902_100559.json
│   │   │   ├── risk3_88612486000160_20260902_100600.json
│   │   │   ├── risk3_88887021000111_20260902_100601.json
│   │   │   ├── risk3_89435598000155_20260902_100601.json
│   │   │   ├── risk3_89637490000145_20260902_100602.json
│   │   │   ├── risk3_90108184000109_20260902_100603.json
│   │   │   ├── risk3_90329178000173_20260902_100604.json
│   │   │   ├── risk3_90406117000162_20260902_100607.json
│   │   │   ├── risk3_90771833000149_20260902_100608.json
│   │   │   ├── risk3_90848052000105_20260902_100609.json
│   │   │   ├── risk3_91362590000158_20260902_100609.json
│   │   │   ├── risk3_91950261000128_20260902_100610.json
│   │   │   ├── risk3_92156777000168_20260902_100611.json
│   │   │   ├── risk3_92632512000199_20260902_100612.json
│   │   │   ├── risk3_93028173000107_20260902_100613.json
│   │   │   ├── risk3_93384311000182_20260902_100614.json
│   │   │   ├── risk3_93640506000146_20260902_100614.json
│   │   │   ├── risk3_93866531000142_20260902_100615.json
│   │   │   ├── risk3_94784543000190_20260902_100617.json
│   │   │   ├── risk3_94819729000138_20260902_100618.json
│   │   │   ├── risk3_94846599000122_20260902_100619.json
│   │   │   ├── risk3_94902509000173_20260902_100620.json
│   │   │   ├── risk3_95370078000104_20260902_100621.json
│   │   │   ├── risk3_95448486000212_20260902_100621.json
│   │   │   ├── risk3_95818399000129_20260902_100622.json
│   │   │   ├── risk3_95837316000149_20260902_100623.json
│   │   │   ├── risk3_95851390000110_20260902_100624.json
│   │   │   ├── risk3_96203393000100_20260902_100625.json
│   │   │   ├── risk3_97192256000180_20260902_100626.json
│   │   │   ├── risk3_97201362002550_20260902_100627.json
│   │   │   ├── risk3_97748958000105_20260902_100627.json
│   │   │   └── risk3_97837181000147_20260902_100628.json
│   │   ├── salesforce_raw/
│   │   └── snapshots_fontes/
│   │       ├── bureau/
│   │       │   └── raw_bureau_BUR_20260910_154515.parquet
│   │       ├── denodo/
│   │       │   └── raw_contratos_CTR_20260910_154423.parquet
│   │       ├── garantias/
│   │       │   └── raw_garantias_20260910.parquet
│   │       ├── mtm/
│   │       │   └── raw_mtm_20260910_data.csv
│   │       ├── receita/
│   │       │   └── raw_receita_20260910.json
│   │       └── salesforce/
│   │           └── raw_salesforce_20260910_salesforce.xlsx
│   ├── gold/
│   │   └── visao_operacional_negocio/
│   │       ├── Visao_Operacional_BDC_20260910.csv
│   │       ├── Visao_Operacional_BDC_20260910.parquet
│   │       ├── Visao_Operacional_BDC_LATEST.csv
│   │       └── Visao_Operacional_BDC_LATEST.parquet
│   ├── relational/
│   │   ├── configs/
│   │   │   └── enquadramento_consumidores_202609.csv
│   │   ├── control/
│   │   │   ├── ctl_campo_origem.parquet
│   │   │   └── ctl_documento.parquet
│   │   ├── dimensions/
│   │   │   └── contrapartes/
│   │   │       ├── dim_contraparte.parquet
│   │   │       ├── dim_contraparte_DIM_CTR_20260910_154541.csv
│   │   │       └── dim_contraparte_DIM_CTR_20260910_154541.parquet
│   │   └── facts/
│   │       ├── alertas/
│   │       │   ├── fato_alerta_credito.csv
│   │       │   └── fato_alerta_credito.parquet
│   │       ├── credito/
│   │       │   ├── fato_analise_credito.csv
│   │       │   └── fato_analise_credito.parquet
│   │       ├── garantias/
│   │       │   ├── fato_garantia.csv
│   │       │   ├── fato_garantia.parquet
│   │       │   ├── fato_garantia_F_GAR_20260910_154544.csv
│   │       │   └── fato_garantia_F_GAR_20260910_154544.parquet
│   │       ├── reconciliacao/
│   │       │   ├── fato_reconciliacao_contrato_mtm.csv
│   │       │   ├── fato_reconciliacao_contrato_mtm.parquet
│   │       │   ├── fato_reconciliacao_fichas_salesforce.csv
│   │       │   └── fato_reconciliacao_fichas_salesforce.parquet
│   │       └── risco/
│   │           ├── fato_exposicao_risco_LATEST.csv
│   │           ├── fato_exposicao_risco_LATEST.parquet
│   │           ├── fato_exposicao_risco_RSK_20260910_154553.csv
│   │           └── fato_exposicao_risco_RSK_20260910_154553.parquet
│   ├── silver/
│   │   ├── alertas_credito/
│   │   │   ├── alertas_cadastrais_receita_REC_20260910_154513.csv
│   │   │   ├── alertas_cadastrais_receita_REC_20260910_154513.parquet
│   │   │   ├── alertas_garantias_F_GAR_20260910_154544.csv
│   │   │   ├── alertas_garantias_F_GAR_20260910_154544.parquet
│   │   │   ├── alertas_reconciliacao_REC_MTM_DENODO_20260910_154554.csv
│   │   │   ├── alertas_reconciliacao_REC_MTM_DENODO_20260910_154554.parquet
│   │   │   ├── alertas_reconciliacao_sf_REC_SF_20260910_154554.csv
│   │   │   └── alertas_reconciliacao_sf_REC_SF_20260910_154554.parquet
│   │   ├── ctl_validacao_qualidade_credito/
│   │   │   ├── pendencias_FATO_ANL_20260910_154543.csv
│   │   │   └── pendencias_FATO_ANL_20260910_154543.parquet
│   │   ├── denodo_contratos_padronizados/
│   │   │   ├── contratos_correntes_202401.csv
│   │   │   ├── contratos_correntes_202401.parquet
│   │   │   ├── contratos_correntes_202402.csv
│   │   │   ├── contratos_correntes_202402.parquet
│   │   │   ├── contratos_correntes_202403.csv
│   │   │   ├── contratos_correntes_202403.parquet
│   │   │   ├── contratos_correntes_202404.csv
│   │   │   ├── contratos_correntes_202404.parquet
│   │   │   ├── contratos_correntes_202405.csv
│   │   │   ├── contratos_correntes_202405.parquet
│   │   │   ├── contratos_correntes_202406.csv
│   │   │   ├── contratos_correntes_202406.parquet
│   │   │   ├── contratos_correntes_202407.csv
│   │   │   ├── contratos_correntes_202407.parquet
│   │   │   ├── contratos_correntes_202408.csv
│   │   │   ├── contratos_correntes_202408.parquet
│   │   │   ├── contratos_correntes_202409.csv
│   │   │   ├── contratos_correntes_202409.parquet
│   │   │   ├── contratos_correntes_202410.csv
│   │   │   ├── contratos_correntes_202410.parquet
│   │   │   ├── contratos_correntes_202411.csv
│   │   │   ├── contratos_correntes_202411.parquet
│   │   │   ├── contratos_correntes_202412.csv
│   │   │   ├── contratos_correntes_202412.parquet
│   │   │   ├── contratos_correntes_202501.csv
│   │   │   ├── contratos_correntes_202501.parquet
│   │   │   ├── contratos_correntes_202502.csv
│   │   │   ├── contratos_correntes_202502.parquet
│   │   │   ├── contratos_correntes_202503.csv
│   │   │   ├── contratos_correntes_202503.parquet
│   │   │   ├── contratos_correntes_202504.csv
│   │   │   ├── contratos_correntes_202504.parquet
│   │   │   ├── contratos_correntes_202505.csv
│   │   │   ├── contratos_correntes_202505.parquet
│   │   │   ├── contratos_correntes_202506.csv
│   │   │   ├── contratos_correntes_202506.parquet
│   │   │   ├── contratos_correntes_202507.csv
│   │   │   ├── contratos_correntes_202507.parquet
│   │   │   ├── contratos_correntes_202508.csv
│   │   │   ├── contratos_correntes_202508.parquet
│   │   │   ├── contratos_correntes_202509.csv
│   │   │   ├── contratos_correntes_202509.parquet
│   │   │   ├── contratos_correntes_202510.csv
│   │   │   ├── contratos_correntes_202510.parquet
│   │   │   ├── contratos_correntes_202511.csv
│   │   │   ├── contratos_correntes_202511.parquet
│   │   │   ├── contratos_correntes_202512.csv
│   │   │   ├── contratos_correntes_202512.parquet
│   │   │   ├── contratos_correntes_202601.csv
│   │   │   ├── contratos_correntes_202601.parquet
│   │   │   ├── contratos_correntes_202602.csv
│   │   │   ├── contratos_correntes_202602.parquet
│   │   │   ├── contratos_correntes_202603.csv
│   │   │   ├── contratos_correntes_202603.parquet
│   │   │   ├── contratos_correntes_202604.csv
│   │   │   ├── contratos_correntes_202604.parquet
│   │   │   ├── contratos_correntes_202605.csv
│   │   │   ├── contratos_correntes_202605.parquet
│   │   │   ├── contratos_correntes_202606.csv
│   │   │   ├── contratos_correntes_202606.parquet
│   │   │   ├── contratos_correntes_202607.csv
│   │   │   ├── contratos_correntes_202607.parquet
│   │   │   ├── contratos_correntes_202608.csv
│   │   │   ├── contratos_correntes_202608.parquet
│   │   │   ├── contratos_correntes_202609.csv
│   │   │   ├── contratos_correntes_202609.parquet
│   │   │   ├── contratos_correntes_202610.csv
│   │   │   ├── contratos_correntes_202610.parquet
│   │   │   ├── contratos_correntes_202611.csv
│   │   │   ├── contratos_correntes_202611.parquet
│   │   │   ├── contratos_correntes_202612.csv
│   │   │   ├── contratos_correntes_202612.parquet
│   │   │   ├── contratos_correntes_202701.csv
│   │   │   ├── contratos_correntes_202701.parquet
│   │   │   ├── contratos_correntes_202702.csv
│   │   │   ├── contratos_correntes_202702.parquet
│   │   │   ├── contratos_correntes_202703.csv
│   │   │   ├── contratos_correntes_202703.parquet
│   │   │   ├── contratos_correntes_202704.csv
│   │   │   ├── contratos_correntes_202704.parquet
│   │   │   ├── contratos_correntes_202705.csv
│   │   │   ├── contratos_correntes_202705.parquet
│   │   │   ├── contratos_correntes_202706.csv
│   │   │   ├── contratos_correntes_202706.parquet
│   │   │   ├── contratos_correntes_202707.csv
│   │   │   ├── contratos_correntes_202707.parquet
│   │   │   ├── contratos_correntes_202708.csv
│   │   │   ├── contratos_correntes_202708.parquet
│   │   │   ├── contratos_correntes_202709.csv
│   │   │   ├── contratos_correntes_202709.parquet
│   │   │   ├── contratos_correntes_202710.csv
│   │   │   ├── contratos_correntes_202710.parquet
│   │   │   ├── contratos_correntes_202711.csv
│   │   │   ├── contratos_correntes_202711.parquet
│   │   │   ├── contratos_correntes_202712.csv
│   │   │   ├── contratos_correntes_202712.parquet
│   │   │   ├── contratos_correntes_202801.csv
│   │   │   ├── contratos_correntes_202801.parquet
│   │   │   ├── contratos_correntes_202802.csv
│   │   │   ├── contratos_correntes_202802.parquet
│   │   │   ├── contratos_correntes_202803.csv
│   │   │   ├── contratos_correntes_202803.parquet
│   │   │   ├── contratos_correntes_202804.csv
│   │   │   ├── contratos_correntes_202804.parquet
│   │   │   ├── contratos_correntes_202805.csv
│   │   │   ├── contratos_correntes_202805.parquet
│   │   │   ├── contratos_correntes_202806.csv
│   │   │   ├── contratos_correntes_202806.parquet
│   │   │   ├── contratos_correntes_202807.csv
│   │   │   ├── contratos_correntes_202807.parquet
│   │   │   ├── contratos_correntes_202808.csv
│   │   │   ├── contratos_correntes_202808.parquet
│   │   │   ├── contratos_correntes_202809.csv
│   │   │   ├── contratos_correntes_202809.parquet
│   │   │   ├── contratos_correntes_202810.csv
│   │   │   ├── contratos_correntes_202810.parquet
│   │   │   ├── contratos_correntes_202811.csv
│   │   │   ├── contratos_correntes_202811.parquet
│   │   │   ├── contratos_correntes_202812.csv
│   │   │   ├── contratos_correntes_202812.parquet
│   │   │   ├── contratos_correntes_202901.csv
│   │   │   ├── contratos_correntes_202901.parquet
│   │   │   ├── contratos_correntes_202902.csv
│   │   │   ├── contratos_correntes_202902.parquet
│   │   │   ├── contratos_correntes_202903.csv
│   │   │   ├── contratos_correntes_202903.parquet
│   │   │   ├── contratos_correntes_202904.csv
│   │   │   ├── contratos_correntes_202904.parquet
│   │   │   ├── contratos_correntes_202905.csv
│   │   │   ├── contratos_correntes_202905.parquet
│   │   │   ├── contratos_correntes_202906.csv
│   │   │   ├── contratos_correntes_202906.parquet
│   │   │   ├── contratos_correntes_202907.csv
│   │   │   ├── contratos_correntes_202907.parquet
│   │   │   ├── contratos_correntes_202908.csv
│   │   │   ├── contratos_correntes_202908.parquet
│   │   │   ├── contratos_correntes_202909.csv
│   │   │   ├── contratos_correntes_202909.parquet
│   │   │   ├── contratos_correntes_202910.csv
│   │   │   ├── contratos_correntes_202910.parquet
│   │   │   ├── contratos_correntes_202911.csv
│   │   │   ├── contratos_correntes_202911.parquet
│   │   │   ├── contratos_correntes_202912.csv
│   │   │   ├── contratos_correntes_202912.parquet
│   │   │   ├── contratos_correntes_203001.csv
│   │   │   ├── contratos_correntes_203001.parquet
│   │   │   ├── contratos_correntes_203002.csv
│   │   │   ├── contratos_correntes_203002.parquet
│   │   │   ├── contratos_correntes_203003.csv
│   │   │   ├── contratos_correntes_203003.parquet
│   │   │   ├── contratos_correntes_203004.csv
│   │   │   ├── contratos_correntes_203004.parquet
│   │   │   ├── contratos_correntes_203005.csv
│   │   │   ├── contratos_correntes_203005.parquet
│   │   │   ├── contratos_correntes_203006.csv
│   │   │   ├── contratos_correntes_203006.parquet
│   │   │   ├── contratos_correntes_203007.csv
│   │   │   ├── contratos_correntes_203007.parquet
│   │   │   ├── contratos_correntes_203008.csv
│   │   │   ├── contratos_correntes_203008.parquet
│   │   │   ├── contratos_correntes_203009.csv
│   │   │   ├── contratos_correntes_203009.parquet
│   │   │   ├── contratos_correntes_203010.csv
│   │   │   ├── contratos_correntes_203010.parquet
│   │   │   ├── contratos_correntes_203011.csv
│   │   │   ├── contratos_correntes_203011.parquet
│   │   │   ├── contratos_correntes_203012.csv
│   │   │   ├── contratos_correntes_203012.parquet
│   │   │   ├── contratos_correntes_203101.csv
│   │   │   ├── contratos_correntes_203101.parquet
│   │   │   ├── contratos_correntes_203102.csv
│   │   │   ├── contratos_correntes_203102.parquet
│   │   │   ├── contratos_correntes_203103.csv
│   │   │   ├── contratos_correntes_203103.parquet
│   │   │   ├── contratos_correntes_203104.csv
│   │   │   ├── contratos_correntes_203104.parquet
│   │   │   ├── contratos_correntes_203105.csv
│   │   │   ├── contratos_correntes_203105.parquet
│   │   │   ├── contratos_correntes_203106.csv
│   │   │   ├── contratos_correntes_203106.parquet
│   │   │   ├── contratos_correntes_203107.csv
│   │   │   ├── contratos_correntes_203107.parquet
│   │   │   ├── contratos_correntes_203108.csv
│   │   │   ├── contratos_correntes_203108.parquet
│   │   │   ├── contratos_correntes_203109.csv
│   │   │   ├── contratos_correntes_203109.parquet
│   │   │   ├── contratos_correntes_203110.csv
│   │   │   ├── contratos_correntes_203110.parquet
│   │   │   ├── contratos_correntes_203111.csv
│   │   │   ├── contratos_correntes_203111.parquet
│   │   │   ├── contratos_correntes_203112.csv
│   │   │   ├── contratos_correntes_203112.parquet
│   │   │   ├── contratos_correntes_203201.csv
│   │   │   ├── contratos_correntes_203201.parquet
│   │   │   ├── contratos_correntes_203202.csv
│   │   │   ├── contratos_correntes_203202.parquet
│   │   │   ├── contratos_correntes_203203.csv
│   │   │   ├── contratos_correntes_203203.parquet
│   │   │   ├── contratos_correntes_203204.csv
│   │   │   ├── contratos_correntes_203204.parquet
│   │   │   ├── contratos_correntes_203205.csv
│   │   │   ├── contratos_correntes_203205.parquet
│   │   │   ├── contratos_correntes_203206.csv
│   │   │   ├── contratos_correntes_203206.parquet
│   │   │   ├── contratos_correntes_203207.csv
│   │   │   ├── contratos_correntes_203207.parquet
│   │   │   ├── contratos_correntes_203208.csv
│   │   │   ├── contratos_correntes_203208.parquet
│   │   │   ├── contratos_correntes_203209.csv
│   │   │   ├── contratos_correntes_203209.parquet
│   │   │   ├── contratos_correntes_203210.csv
│   │   │   ├── contratos_correntes_203210.parquet
│   │   │   ├── contratos_correntes_203211.csv
│   │   │   ├── contratos_correntes_203211.parquet
│   │   │   ├── contratos_correntes_203212.csv
│   │   │   ├── contratos_correntes_203212.parquet
│   │   │   ├── contratos_correntes_203301.csv
│   │   │   ├── contratos_correntes_203301.parquet
│   │   │   ├── contratos_correntes_203302.csv
│   │   │   ├── contratos_correntes_203302.parquet
│   │   │   ├── contratos_correntes_203303.csv
│   │   │   ├── contratos_correntes_203303.parquet
│   │   │   ├── contratos_correntes_203304.csv
│   │   │   ├── contratos_correntes_203304.parquet
│   │   │   ├── contratos_correntes_203305.csv
│   │   │   ├── contratos_correntes_203305.parquet
│   │   │   ├── contratos_correntes_203306.csv
│   │   │   ├── contratos_correntes_203306.parquet
│   │   │   ├── contratos_correntes_203307.csv
│   │   │   ├── contratos_correntes_203307.parquet
│   │   │   ├── contratos_correntes_203308.csv
│   │   │   ├── contratos_correntes_203308.parquet
│   │   │   ├── contratos_correntes_203309.csv
│   │   │   ├── contratos_correntes_203309.parquet
│   │   │   ├── contratos_correntes_203310.csv
│   │   │   ├── contratos_correntes_203310.parquet
│   │   │   ├── contratos_correntes_203311.csv
│   │   │   ├── contratos_correntes_203311.parquet
│   │   │   ├── contratos_correntes_203312.csv
│   │   │   ├── contratos_correntes_203312.parquet
│   │   │   ├── contratos_correntes_203401.csv
│   │   │   ├── contratos_correntes_203401.parquet
│   │   │   ├── contratos_correntes_203402.csv
│   │   │   ├── contratos_correntes_203402.parquet
│   │   │   ├── contratos_correntes_203403.csv
│   │   │   ├── contratos_correntes_203403.parquet
│   │   │   ├── contratos_correntes_203404.csv
│   │   │   ├── contratos_correntes_203404.parquet
│   │   │   ├── contratos_correntes_203405.csv
│   │   │   ├── contratos_correntes_203405.parquet
│   │   │   ├── contratos_correntes_203406.csv
│   │   │   ├── contratos_correntes_203406.parquet
│   │   │   ├── contratos_correntes_203407.csv
│   │   │   ├── contratos_correntes_203407.parquet
│   │   │   ├── contratos_correntes_203408.csv
│   │   │   ├── contratos_correntes_203408.parquet
│   │   │   ├── contratos_correntes_203409.csv
│   │   │   ├── contratos_correntes_203409.parquet
│   │   │   ├── contratos_correntes_203410.csv
│   │   │   ├── contratos_correntes_203410.parquet
│   │   │   ├── contratos_correntes_203411.csv
│   │   │   ├── contratos_correntes_203411.parquet
│   │   │   ├── contratos_correntes_203412.csv
│   │   │   ├── contratos_correntes_203412.parquet
│   │   │   ├── contratos_correntes_203501.csv
│   │   │   ├── contratos_correntes_203501.parquet
│   │   │   ├── contratos_correntes_203502.csv
│   │   │   ├── contratos_correntes_203502.parquet
│   │   │   ├── contratos_correntes_203503.csv
│   │   │   ├── contratos_correntes_203503.parquet
│   │   │   ├── contratos_correntes_203504.csv
│   │   │   ├── contratos_correntes_203504.parquet
│   │   │   ├── contratos_correntes_203505.csv
│   │   │   ├── contratos_correntes_203505.parquet
│   │   │   ├── contratos_correntes_203506.csv
│   │   │   ├── contratos_correntes_203506.parquet
│   │   │   ├── contratos_correntes_203507.csv
│   │   │   ├── contratos_correntes_203507.parquet
│   │   │   ├── contratos_correntes_203508.csv
│   │   │   ├── contratos_correntes_203508.parquet
│   │   │   ├── contratos_correntes_203509.csv
│   │   │   ├── contratos_correntes_203509.parquet
│   │   │   ├── contratos_correntes_203510.csv
│   │   │   ├── contratos_correntes_203510.parquet
│   │   │   ├── contratos_correntes_203511.csv
│   │   │   ├── contratos_correntes_203511.parquet
│   │   │   ├── contratos_correntes_203512.csv
│   │   │   ├── contratos_correntes_203512.parquet
│   │   │   ├── contratos_correntes_203601.csv
│   │   │   ├── contratos_correntes_203601.parquet
│   │   │   ├── contratos_correntes_203602.csv
│   │   │   ├── contratos_correntes_203602.parquet
│   │   │   ├── contratos_correntes_203603.csv
│   │   │   ├── contratos_correntes_203603.parquet
│   │   │   ├── contratos_correntes_203604.csv
│   │   │   ├── contratos_correntes_203604.parquet
│   │   │   ├── contratos_correntes_203605.csv
│   │   │   ├── contratos_correntes_203605.parquet
│   │   │   ├── contratos_correntes_203606.csv
│   │   │   ├── contratos_correntes_203606.parquet
│   │   │   ├── contratos_correntes_203607.csv
│   │   │   ├── contratos_correntes_203607.parquet
│   │   │   ├── contratos_correntes_203608.csv
│   │   │   ├── contratos_correntes_203608.parquet
│   │   │   ├── contratos_correntes_203609.csv
│   │   │   ├── contratos_correntes_203609.parquet
│   │   │   ├── contratos_correntes_203610.csv
│   │   │   ├── contratos_correntes_203610.parquet
│   │   │   ├── contratos_correntes_203611.csv
│   │   │   ├── contratos_correntes_203611.parquet
│   │   │   ├── contratos_correntes_203612.csv
│   │   │   ├── contratos_correntes_203612.parquet
│   │   │   ├── contratos_correntes_203701.csv
│   │   │   ├── contratos_correntes_203701.parquet
│   │   │   ├── contratos_correntes_203702.csv
│   │   │   ├── contratos_correntes_203702.parquet
│   │   │   ├── contratos_correntes_203703.csv
│   │   │   ├── contratos_correntes_203703.parquet
│   │   │   ├── contratos_correntes_203704.csv
│   │   │   ├── contratos_correntes_203704.parquet
│   │   │   ├── contratos_correntes_203705.csv
│   │   │   ├── contratos_correntes_203705.parquet
│   │   │   ├── contratos_correntes_203706.csv
│   │   │   ├── contratos_correntes_203706.parquet
│   │   │   ├── contratos_correntes_203707.csv
│   │   │   ├── contratos_correntes_203707.parquet
│   │   │   ├── contratos_correntes_203708.csv
│   │   │   ├── contratos_correntes_203708.parquet
│   │   │   ├── contratos_correntes_203709.csv
│   │   │   ├── contratos_correntes_203709.parquet
│   │   │   ├── contratos_correntes_203710.csv
│   │   │   ├── contratos_correntes_203710.parquet
│   │   │   ├── contratos_correntes_203711.csv
│   │   │   ├── contratos_correntes_203711.parquet
│   │   │   ├── contratos_correntes_203712.csv
│   │   │   ├── contratos_correntes_203712.parquet
│   │   │   ├── contratos_correntes_203801.csv
│   │   │   ├── contratos_correntes_203801.parquet
│   │   │   ├── contratos_correntes_203802.csv
│   │   │   ├── contratos_correntes_203802.parquet
│   │   │   ├── contratos_correntes_203803.csv
│   │   │   ├── contratos_correntes_203803.parquet
│   │   │   ├── contratos_correntes_203804.csv
│   │   │   ├── contratos_correntes_203804.parquet
│   │   │   ├── contratos_correntes_203805.csv
│   │   │   ├── contratos_correntes_203805.parquet
│   │   │   ├── contratos_correntes_203806.csv
│   │   │   ├── contratos_correntes_203806.parquet
│   │   │   ├── contratos_correntes_203807.csv
│   │   │   ├── contratos_correntes_203807.parquet
│   │   │   ├── contratos_correntes_203808.csv
│   │   │   ├── contratos_correntes_203808.parquet
│   │   │   ├── contratos_correntes_203809.csv
│   │   │   ├── contratos_correntes_203809.parquet
│   │   │   ├── contratos_correntes_203810.csv
│   │   │   ├── contratos_correntes_203810.parquet
│   │   │   ├── contratos_correntes_203811.csv
│   │   │   ├── contratos_correntes_203811.parquet
│   │   │   ├── contratos_correntes_203812.csv
│   │   │   ├── contratos_correntes_203812.parquet
│   │   │   ├── contratos_correntes_203901.csv
│   │   │   ├── contratos_correntes_203901.parquet
│   │   │   ├── contratos_correntes_203902.csv
│   │   │   ├── contratos_correntes_203902.parquet
│   │   │   ├── contratos_correntes_203903.csv
│   │   │   ├── contratos_correntes_203903.parquet
│   │   │   ├── contratos_correntes_203904.csv
│   │   │   ├── contratos_correntes_203904.parquet
│   │   │   ├── contratos_correntes_203905.csv
│   │   │   ├── contratos_correntes_203905.parquet
│   │   │   ├── contratos_correntes_203906.csv
│   │   │   ├── contratos_correntes_203906.parquet
│   │   │   ├── contratos_correntes_203907.csv
│   │   │   ├── contratos_correntes_203907.parquet
│   │   │   ├── contratos_correntes_203908.csv
│   │   │   ├── contratos_correntes_203908.parquet
│   │   │   ├── contratos_correntes_203909.csv
│   │   │   ├── contratos_correntes_203909.parquet
│   │   │   ├── contratos_correntes_203910.csv
│   │   │   ├── contratos_correntes_203910.parquet
│   │   │   ├── contratos_correntes_203911.csv
│   │   │   ├── contratos_correntes_203911.parquet
│   │   │   ├── contratos_correntes_203912.csv
│   │   │   ├── contratos_correntes_203912.parquet
│   │   │   ├── contratos_correntes_204001.csv
│   │   │   ├── contratos_correntes_204001.parquet
│   │   │   ├── contratos_correntes_204002.csv
│   │   │   ├── contratos_correntes_204002.parquet
│   │   │   ├── contratos_correntes_204003.csv
│   │   │   ├── contratos_correntes_204003.parquet
│   │   │   ├── contratos_correntes_204004.csv
│   │   │   ├── contratos_correntes_204004.parquet
│   │   │   ├── contratos_correntes_204005.csv
│   │   │   ├── contratos_correntes_204005.parquet
│   │   │   ├── contratos_correntes_204006.csv
│   │   │   ├── contratos_correntes_204006.parquet
│   │   │   ├── contratos_correntes_204007.csv
│   │   │   ├── contratos_correntes_204007.parquet
│   │   │   ├── contratos_correntes_204008.csv
│   │   │   ├── contratos_correntes_204008.parquet
│   │   │   ├── contratos_correntes_204009.csv
│   │   │   ├── contratos_correntes_204009.parquet
│   │   │   ├── contratos_correntes_204010.csv
│   │   │   ├── contratos_correntes_204010.parquet
│   │   │   ├── contratos_correntes_204011.csv
│   │   │   ├── contratos_correntes_204011.parquet
│   │   │   ├── contratos_correntes_204012.csv
│   │   │   └── contratos_correntes_204012.parquet
│   │   ├── denodo_contratos_silver/
│   │   │   ├── contratos_correntes.csv
│   │   │   └── contratos_correntes.parquet
│   │   ├── documentos_classificados/
│   │   │   ├── documentos_classificados__BDC_20260910_153728.csv
│   │   │   ├── documentos_classificados__BDC_20260910_153728.parquet
│   │   │   ├── documentos_classificados__BDC_20260910_154203.csv
│   │   │   └── documentos_classificados__BDC_20260910_154203.parquet
│   │   ├── fato_bureau_silver/
│   │   │   ├── fato_bureau_silver.csv
│   │   │   └── fato_bureau_silver.parquet
│   │   ├── fichas_comercializadoras_extraidas/
│   │   │   ├── fichas_comercializadoras_extraidas.csv
│   │   │   └── fichas_comercializadoras_extraidas.parquet
│   │   ├── fichas_consumidores_extraidas/
│   │   │   ├── fichas_consumidores_extraidas.csv
│   │   │   └── fichas_consumidores_extraidas.parquet
│   │   ├── garantias_silver/
│   │   │   ├── garantia_silver.csv
│   │   │   └── garantia_silver.parquet
│   │   ├── mtm_consolidado_silver/
│   │   │   ├── mtm_agregado_contraparte.parquet
│   │   │   ├── mtm_agregado_contraparte_MTM_20260910_154446.csv
│   │   │   └── mtm_agregado_contraparte_MTM_20260910_154446.parquet
│   │   ├── receita_silver/
│   │   │   ├── receita_cadastral_silver.parquet
│   │   │   ├── receita_cadastral_silver_REC_20260910_154513.csv
│   │   │   └── receita_cadastral_silver_REC_20260910_154513.parquet
│   │   ├── reconciliacao_contratos_mtm/
│   │   │   ├── fato_reconciliacao_contrato_mtm.csv
│   │   │   └── fato_reconciliacao_contrato_mtm.parquet
│   │   └── salesforce_silver/
│   │       ├── account/
│   │       │   ├── salesforce_account.csv
│   │       │   └── salesforce_account.parquet
│   │       ├── chamado/
│   │       │   ├── salesforce_chamado.csv
│   │       │   └── salesforce_chamado.parquet
│   │       ├── contrato/
│   │       │   ├── salesforce_contrato.csv
│   │       │   └── salesforce_contrato.parquet
│   │       └── cotacao/
│   │           ├── salesforce_cotacao.csv
│   │           └── salesforce_cotacao.parquet
│   └── staging/
│       ├── fichas_comercializadoras/
│       │   ├── 2W ENERGIA 05_07_2022__3caa8318.xlsx
│       │   ├── 2W ENERGIA 05_07_2022__padrao_2__08773135000100__31122021__3caa8318.xlsx
│       │   ├── 2W ENERGIA_28.08.2024__c1d3e2e9.xlsx
│       │   ├── 2W ENERGIA_28.08.2024__padrao_3__08773135000100__30092023__c1d3e2e9.xlsx
│       │   ├── 2W_13062023 - Copia__5ffd71f6.xlsx
│       │   ├── 2W_13062023 - Copia__padrao_6__08773135000100__31122022__5ffd71f6.xlsx
│       │   ├── 2W_18_06_2021__945043a6.xlsx
│       │   ├── 2W_18_06_2021__padrao_2__08773135000100__31122020__945043a6.xlsx
│       │   ├── ABC 14072026__c231ff50.xlsx
│       │   ├── ABC 14072026__padrao_6__29198324000168__31122025__c231ff50.xlsx
│       │   ├── ABC 29.07.2024__5361ed62.xlsx
│       │   ├── ABC 29.07.2024__padrao_3__29198324000168__31122023__5361ed62.xlsx
│       │   ├── ABC BRASIL 15102025__d50b1666.xlsx
│       │   ├── ABC BRASIL 15102025__padrao_3__29198324000168__31122024__d50b1666.xlsx
│       │   ├── ADN 02062026__b8df8c05.xlsx
│       │   ├── ADN 02062026__padrao_6__20591154000102__31122025__b8df8c05.xlsx
│       │   ├── AES BRASIL 09_05_2022 TESTE GRUPO__64ffe30f.xlsx
│       │   ├── AES_05012024__7a4ec190.xlsx
│       │   ├── AES_05012024__padrao_3__43412008000178__31122022__7a4ec190.xlsx
│       │   ├── AES_19.06.2024__bb3ce3d9.xlsx
│       │   ├── AES_19.06.2024__padrao_3__43412008000178__31122023__bb3ce3d9.xlsx
│       │   ├── AGE COMERCIALIZADORA 30062026__3e8ceac0.xlsx
│       │   ├── AGE COMERCIALIZADORA 30062026__padrao_6__14167541000113__31122025__3e8ceac0.xlsx
│       │   ├── AGORA ENERGIA 09062026__e095038d.xlsx
│       │   ├── AGORA ENERGIA 09062026__padrao_6__15623286000139__31122025__e095038d.xlsx
│       │   ├── AGORA21.05.2024__6168402a.xlsx
│       │   ├── AGORA21.05.2024__padrao_6__15623286000139__31122023__6168402a.xlsx
│       │   ├── AGROENERGIA _10_05_2021__1e49e51e.xlsx
│       │   ├── AGROENERGIA _10_05_2021__padrao_2__12422540000142__31122020__1e49e51e.xlsx
│       │   ├── ALBIOMA 09072026__fb0d87b8.xlsx
│       │   ├── ALBIOMA 09072026__padrao_6__29915125000123__31122025__fb0d87b8.xlsx
│       │   ├── ALBIOMA CODORA__9c3a6d7a.xlsx
│       │   ├── ALBIOMA CODORA__padrao_6__07966116000129__31122025__9c3a6d7a.xlsx
│       │   ├── ALCAST_12.07.2024__f1bb56e9.xlsx
│       │   ├── ALCAST_12.07.2024__padrao_3__34980728000149__31122023__f1bb56e9.xlsx
│       │   ├── ALIANCA_GERACAO 28052026__86a7ff62.xlsx
│       │   ├── ALIANCA_GERACAO 28052026__padrao_6__12009135000105__31122025__86a7ff62.xlsx
│       │   ├── ALIANÇA 20_07_2022__4bef1e0a.xlsx
│       │   ├── ALIANÇA 20_07_2022__padrao_2__12009135000105__31122021__4bef1e0a.xlsx
│       │   ├── ALIANÇA GERAÇÃO RATING 06022026__c8cace32.xlsx
│       │   ├── ALIANÇA GERAÇÃO RATING 06022026__padrao_6__12009135000105__31122024__c8cace32.xlsx
│       │   ├── ALUPAR 19112024__10a891eb.xlsx
│       │   ├── ALUPAR 19112024__padrao_3__08364948000138__31122023__10a891eb.xlsx
│       │   ├── ALUPAR_06062025__d0cfa612.xlsx
│       │   ├── ALUPAR_06062025__padrao_3__08364948000138__31122024__d0cfa612.xlsx
│       │   ├── AMAGGI 11_07_2022__24864266.xlsx
│       │   ├── AMAGGI 11_07_2022__padrao_2__16587133000146__31122021__24864266.xlsx
│       │   ├── AMAGGI 26062025__0c2e141b.xlsx
│       │   ├── AMAGGI RATING 05022026__4c058416.xlsx
│       │   ├── AMAGGI RATING 05022026__padrao_6__16587133000146__31122024__4c058416.xlsx
│       │   ├── AMBAR 11122023__118d9d11.xlsx
│       │   ├── AMBAR 11122023__padrao_3__31627849000113__31122022__118d9d11.xlsx
│       │   ├── AMBAR 26_04_2022__7cf8e401.xlsx
│       │   ├── AMBAR 26_04_2022__padrao_2__31627849000113__31122021__7cf8e401.xlsx
│       │   ├── AMBAR_29.07.2024__3a55eb58.xlsx
│       │   ├── AMBAR_29.07.2024__padrao_3__31627849000113__31122023__3a55eb58.xlsx
│       │   ├── AMBAR_31_08_2021__53c81f1e.xlsx
│       │   ├── AMBAR_31_08_2021__padrao_2__31627849000113__31122020__53c81f1e.xlsx
│       │   ├── AMERICA_07_06_2021__7e6a0991.xlsx
│       │   ├── AMERICA_07_06_2021__padrao_2__11085823000183__31122020__7e6a0991.xlsx
│       │   ├── AMERICA_20.05.2024__49703718.xlsx
│       │   ├── AMERICA_20.05.2024__padrao_6__11085823000183__31122023__49703718.xlsx
│       │   ├── ANGELIM 09062026__d06c5420.xlsx
│       │   ├── ANGELIM 09062026__padrao_6__19502690000105__31122025__d06c5420.xlsx
│       │   ├── ANGELINA COLOMBO 29072026__e76d1e65.xlsx
│       │   ├── ANGELINA COLOMBO 29072026__padrao_6__35881121000174__31032026__e76d1e65.xlsx
│       │   ├── ANGELINA COLOMBO__662041cd.xlsx
│       │   ├── ANGELINA COLOMBO__padrao_6__35881121000174__31122025__662041cd.xlsx
│       │   ├── APOLLO 08 05 2024__9bf42e45.xlsx
│       │   ├── APOLLO 08 05 2024__padrao_3__25318541000193__31122023__9bf42e45.xlsx
│       │   ├── APOLO 02_05_2022__b9a6f52a.xlsx
│       │   ├── APOLO 02_05_2022__padrao_2__08842785000151__31122021__b9a6f52a.xlsx
│       │   ├── APOLO_24_06_2021__bfaead97.xlsx
│       │   ├── APOLO_24_06_2021__padrao_2__08842785000151__31122020__bfaead97.xlsx
│       │   ├── APTCOM_10052023__9efd7f2c.xlsx
│       │   ├── AQUARIUS 11062026__24dd195b.xlsx
│       │   ├── AQUARIUS 11062026__padrao_6__05350372000161__31122025__24dd195b.xlsx
│       │   ├── ARCELORMITTAL_21.05.2024__8a8eb40c.xlsx
│       │   ├── ARCELORMITTAL_21.05.2024__padrao_3__17469701000177__31122023__8a8eb40c.xlsx
│       │   ├── ARMOR 15082025__56155d1c.xlsx
│       │   ├── ARMOR 15082025__padrao_3__38154005000141__31122024__56155d1c.xlsx
│       │   ├── ARMOR_20.05.2024__0286849f.xlsx
│       │   ├── ARMOR_20.05.2024__padrao_6__38154005000141__31122023__0286849f.xlsx
│       │   ├── ARMOS_07062023__5d33bd0f.xlsx
│       │   ├── ARMOS_07062023__padrao_4__38154005000141__31122022__5d33bd0f.xlsx
│       │   ├── ASOLO 29052026__21a8f211.xlsx
│       │   ├── ASOLO 29052026__padrao_6__41675130000101__31122025__21a8f211.xlsx
│       │   ├── ATHENA 29_08_2022__e076cf16.xlsx
│       │   ├── ATHENA 29_08_2022__padrao_2__31233530000103__31122021__e076cf16.xlsx
│       │   ├── ATIAIA 18082026__7465779d.xlsx
│       │   ├── ATIAIA 18082026__padrao_6__15728576000147__31122025__7465779d.xlsx
│       │   ├── ATIAIA 24062025__5239f515.xlsx
│       │   ├── ATIAIA 24062025__padrao_3__15728576000147__31122024__5239f515.xlsx
│       │   ├── ATIAIA RATING 06022026__17baa2fa.xlsx
│       │   ├── ATIAIA RATING 06022026__padrao_6__15728576000147__31122024__17baa2fa.xlsx
│       │   ├── ATLAS_18022025__7d8dc8e0.xlsx
│       │   ├── ATLAS_18022025__padrao_3__24337192000194__31122023__7d8dc8e0.xlsx
│       │   ├── ATMO 04052026__375dcb8b.xlsx
│       │   ├── ATMO 04052026__padrao_6__11322550000143__31122025__375dcb8b.xlsx
│       │   ├── ATMO 06_05_2022__2f8d89de.xlsx
│       │   ├── ATMO 06_05_2022__padrao_2__11322550000143__31122021__2f8d89de.xlsx
│       │   ├── ATMO 16052025__1__c3b57c83.xlsx
│       │   ├── ATMO 16052025__1__padrao_3__11322550000143__31122024__c3b57c83.xlsx
│       │   ├── ATMO 16052025__9d3f04a9.xlsx
│       │   ├── ATMO 16052025__padrao_3__11322550000224__31122024__9d3f04a9.xlsx
│       │   ├── ATMO 27032026__e6d41510.xlsx
│       │   ├── ATMO 27032026__padrao_6__11322550000143__31122024__e6d41510.xlsx
│       │   ├── ATMO_06.06.2024__179ccc1c.xlsx
│       │   ├── ATMO_06.06.2024__padrao_6__11322550000143__31122023__179ccc1c.xlsx
│       │   ├── ATMO_16062023__555e4f07.xlsx
│       │   ├── ATMO_16062023__padrao_3__11322550000143__31122022__555e4f07.xlsx
│       │   ├── ATMO_31_08_2021__4f162783.xlsx
│       │   ├── ATMO_31_08_2021__padrao_2__11322550000143__31122020__4f162783.xlsx
│       │   ├── ATVOS BRENCO 27072026__196c81e6.xlsx
│       │   ├── ATVOS BRENCO 27072026__padrao_6__08070566000100__31032026__196c81e6.xlsx
│       │   ├── ATVOS PART. 03082026__fdee3e1e.xlsx
│       │   ├── ATVOS PART. 03082026__padrao_6__08070508000178__31032026__fdee3e1e.xlsx
│       │   ├── ATVOS RIO CLARO 31072026__3f8bbb51.xlsx
│       │   ├── ATVOS RIO CLARO 31072026__padrao_6__08598391000108__31032026__3f8bbb51.xlsx
│       │   ├── AUREN (VOTENER) 06_05_2022__7029c96b.xlsx
│       │   ├── AUREN COM 22072026__3d576fdf.xlsx
│       │   ├── AUREN COM 22072026__padrao_6__03984862000194__31122025__3d576fdf.xlsx
│       │   ├── AUREN_13.06.2024__e5bf103e.xlsx
│       │   ├── AUREN_13.06.2024__padrao_3__03984862000194__31122023__e5bf103e.xlsx
│       │   ├── AUREN_16062023__9239e50f.xlsx
│       │   ├── AUREN_16062023__padrao_3__03984862000194__31122022__9239e50f.xlsx
│       │   ├── AUREN_24092025__ad0be7ac.xlsx
│       │   ├── AUREN_24092025__padrao_3__03984862000194__18032025__ad0be7ac.xlsx
│       │   ├── AXIA 24082026__97d31ef6.xlsx
│       │   ├── AXIA 24082026__padrao_6__00001180000126__31122024__97d31ef6.xlsx
│       │   ├── B2R 27_06_2022__48bc53bf.xlsx
│       │   ├── B2R 27_06_2022__padrao_2__32618447000115__31122021__48bc53bf.xlsx
│       │   ├── B2R ENERGIA_20122021__deb25d25.xlsx
│       │   ├── B2R ENERGIA_20122021__padrao_2__32618447000115__31122020__deb25d25.xlsx
│       │   ├── B2R_06.06.2024__11699b5e.xlsx
│       │   ├── B2R_06.06.2024__padrao_3__32618447000620__31122023__11699b5e.xlsx
│       │   ├── B2R_22.05.2024__e75ca729.xlsx
│       │   ├── B2R_22.05.2024__padrao_6__32618447000115__31122023__e75ca729.xlsx
│       │   ├── Banco ABC 05092023__966513b8.xlsx
│       │   ├── Banco ABC 05092023__padrao_3__29198324000168__31122022__966513b8.xlsx
│       │   ├── BANCO BOCOM BBM 25_05_2022__312b14cb.xlsx
│       │   ├── BANCO BTG PACTUAL (GRUPO) 14_07_2022__c445ab91.xlsx
│       │   ├── BARIGUI_17.05.2024__0eb64eae.xlsx
│       │   ├── BARIGUI_17.05.2024__padrao_3__29993083000149__31122023__0eb64eae.xlsx
│       │   ├── BARIGUI_17032023__a0b5182c.xlsx
│       │   ├── BARIGUI_17032023__padrao_4__29993083000149__31122022__a0b5182c.xlsx
│       │   ├── BARRALCOOL 13072026__22d453c5.xlsx
│       │   ├── BARRALCOOL 13072026__padrao_6__33664228000135__31122025__22d453c5.xlsx
│       │   ├── BC 06_05_2022__58170c6c.xlsx
│       │   ├── BC 06_05_2022__padrao_2__18384740000134__31122021__58170c6c.xlsx
│       │   ├── BC COMERCIALIZADORA 27032026__10587ef8.xlsx
│       │   ├── BC COMERCIALIZADORA 27032026__padrao_6__18384740000134__31122024__10587ef8.xlsx
│       │   ├── BC_05042024__693fee93.xlsx
│       │   ├── BC_05042024__padrao_3__18384740000134__31122023__693fee93.xlsx
│       │   ├── BEM 10062026__7a0ff343.xlsx
│       │   ├── BEM 10062026__padrao_6__23412242000198__31122025__7a0ff343.xlsx
│       │   ├── BEP 08_06_2022__da6943c0.xlsx
│       │   ├── BEP 08_06_2022__padrao_2__14555633000170__31122021__da6943c0.xlsx
│       │   ├── BEP 09072025 - Copia__35418ac7.xlsx
│       │   ├── BEP 09072025 - Copia__padrao_3__14555633000170__31122024__35418ac7.xlsx
│       │   ├── BEP 31_08_2021__71a5b8fb.xlsx
│       │   ├── BEP 31_08_2021__padrao_2__14555633000170__31122020__71a5b8fb.xlsx
│       │   ├── BEP ENERGIA RATING 24032026__d51902d4.xlsx
│       │   ├── BEP ENERGIA RATING 24032026__padrao_6__14555633000170__31122025__d51902d4.xlsx
│       │   ├── BEP_16.05.2024__ecaafd9f.xlsx
│       │   ├── BEP_16.05.2024__padrao_6__14555633000170__31122023__ecaafd9f.xlsx
│       │   ├── BEVAP 11082026__3b69096f.xlsx
│       │   ├── BEVAP 11082026__padrao_6__08793343000162__31032026__3b69096f.xlsx
│       │   ├── BEVAP SA RATING 03032026__93905d3c.xlsx
│       │   ├── BEVAP SA RATING 03032026__padrao_6__08793343000162__31032025__93905d3c.xlsx
│       │   ├── BID ENERGY 04_05_2022__e26b3998.xlsx
│       │   ├── BID ENERGY 04_05_2022__padrao_2__14023604000168__31122021__e26b3998.xlsx
│       │   ├── BID_12.06.2024__b0bda683.xlsx
│       │   ├── BID_12.06.2024__padrao_3__14023604000168__31122023__b0bda683.xlsx
│       │   ├── BID_13102023__1cd5db0c.xlsx
│       │   ├── BID_13102023__padrao_3__14023604000168__31122022__1cd5db0c.xlsx
│       │   ├── BIOENERGETICA BOA VISTA RATING 03022026__f1dc9afe.xlsx
│       │   ├── BIOENERGETICA BOA VISTA RATING 03022026__padrao_6__24222394000190__31032025__f1dc9afe.xlsx
│       │   ├── BIOENERGETICA SANTA CRUZ RATING 02022026__86cc5b94.xlsx
│       │   ├── BIOENERGETICA SANTA CRUZ RATING 02022026__padrao_6__10763227000142__31122024__86cc5b94.xlsx
│       │   ├── BIOENERGÉTICA SÃO MARTINHO RATING 020220__9f8e2914.xlsx
│       │   ├── BIOENERGÉTICA SÃO MARTINHO RATING 020220__padrao_6__12291462000194__31032025__9f8e2914.xlsx
│       │   ├── BO ENERGY 04_05_2022__b2a4cc49.xlsx
│       │   ├── BO ENERGY 04_05_2022__padrao_2__12368097000179__31122021__b2a4cc49.xlsx
│       │   ├── BOENERGY_08052023__464ec637.xlsx
│       │   ├── BOENERGY_08052023__padrao_4__12368097000179__31122022__464ec637.xlsx
│       │   ├── BOLT 05092023__a7525c59.xlsx
│       │   ├── BOLT 05092023__padrao_3__13700609000115__31122022__a7525c59.xlsx
│       │   ├── BOLT 06_06_2022__348e71d5.xlsx
│       │   ├── BOLT 06_06_2022__padrao_2__13700609000115__31122021__348e71d5.xlsx
│       │   ├── BOLT_01_09_2021__2eb1e752.xlsx
│       │   ├── BOLT_01_09_2021__padrao_2__13700609000115__31122020__2eb1e752.xlsx
│       │   ├── BOLT_17.05.2024__d8044fcc.xlsx
│       │   ├── BOLT_17.05.2024__padrao_3__13700609000115__31122023__d8044fcc.xlsx
│       │   ├── BOLT_2024__09f8e4b2.xlsx
│       │   ├── BOLT_2024__padrao_3__13700609000115__31122024__09f8e4b2.xlsx
│       │   ├── BOREAL 17_05_2022__bc32ab7b.xlsx
│       │   ├── BOREAL 17_05_2022__padrao_2__30195195000133__31122021__bc32ab7b.xlsx
│       │   ├── BOREAL_01_09_2021__e65de90c.xlsx
│       │   ├── BOREAL_01_09_2021__padrao_2__30195195000133__31122020__e65de90c.xlsx
│       │   ├── BOVEN 27_06_2022__3c276730.xlsx
│       │   ├── BOVEN 27_06_2022__padrao_2__14609649000119__31122021__3c276730.xlsx
│       │   ├── BOVEN 28032024__ad708f73.xlsx
│       │   ├── BOVEN 28032024__padrao_3__14609649000119__31122023__ad708f73.xlsx
│       │   ├── BP COM_04_10_2021__33623173.xlsx
│       │   ├── BP COM_04_10_2021__padrao_2__31864869000108__31032021__33623173.xlsx
│       │   ├── BP Comercializadora_28_01_2022__a56f4172.xlsx
│       │   ├── BP Comercializadora_28_01_2022__padrao_2__31864869000108__31122021__a56f4172.xlsx
│       │   ├── BP ENERGIA_23.07.2024__68a04eba.xlsx
│       │   ├── BP ENERGIA_23.07.2024__padrao_3__31864869000108__31122023__68a04eba.xlsx
│       │   ├── BR ENERGIAS RATING 03022026__5d8e716a.xlsx
│       │   ├── BR ENERGIAS RATING 03022026__padrao_6__07416174000189__31122024__5d8e716a.xlsx
│       │   ├── BRADESCO 04072025__b5b99522.xlsx
│       │   ├── BRADESCO 04072025__padrao_3__07131859000189__17122024__b5b99522.xlsx
│       │   ├── BRADESCO 30072026__be94bc7b.xlsx
│       │   ├── BRADESCO 30072026__padrao_6__07131859000189__31122025__be94bc7b.xlsx
│       │   ├── BRASIL COM 11_07_2022__4a9020dc.xlsx
│       │   ├── BRASIL COM 11_07_2022__padrao_2__13145928000106__31122021__4a9020dc.xlsx
│       │   ├── BRASIL COM_11_06_2021__68d80f92.xlsx
│       │   ├── BRASIL COM_11_06_2021__padrao_2__13145928000106__31122020__68d80f92.xlsx
│       │   ├── BRASIL COM_18_04_2023__0d0d6eee.xlsx
│       │   ├── BRASIL COM_18_04_2023__padrao_3__13145928000106__31122022__0d0d6eee.xlsx
│       │   ├── BRASIL SERVICOS_08_06_2021__30342cfb.xlsx
│       │   ├── BRASIL SERVICOS_08_06_2021__padrao_2__30929117000115__31122020__30342cfb.xlsx
│       │   ├── BRASIL Serviços_18042023__442f5d30.xlsx
│       │   ├── BRASIL Serviços_18042023__padrao_3__30929117000115__31122022__442f5d30.xlsx
│       │   ├── BRASKEN 19 04 2024__6bb2a17d.xlsx
│       │   ├── BRASKEN 19 04 2024__padrao_3__37543498000149__31122023__6bb2a17d.xlsx
│       │   ├── BRAVO 08052026__a3fcc638.xlsx
│       │   ├── BRAVO 08052026__padrao_6__31512081000132__31122025__a3fcc638.xlsx
│       │   ├── BRAVO 11042024__3990468c.xlsx
│       │   ├── BRAVO 11042024__padrao_6__31512081000132__31122023__3990468c.xlsx
│       │   ├── Bravo_2024 (Salvo automaticamente)__7f3677ca.xlsx
│       │   ├── Bravo_2024 (Salvo automaticamente)__padrao_3__31512081000132__31122024__7f3677ca.xlsx
│       │   ├── Bravo_2024__79ec5eb9.xlsx
│       │   ├── BRAVO_25_10_2021__701cdbb9.xlsx
│       │   ├── BRAVO_25_10_2021__padrao_2__31512081000132__31122020__701cdbb9.xlsx
│       │   ├── BRAVO_26052023__45593681.xlsx
│       │   ├── BRAVO_26052023__padrao_3__31512081000132__31122022__45593681.xlsx
│       │   ├── BRF Energia 15072025__0948b34a.xlsx
│       │   ├── BRF Energia 15072025__padrao_3__05449127000106__31122024__0948b34a.xlsx
│       │   ├── BROOKFIELD_01_09_2021__dcc16cbc.xlsx
│       │   ├── BROOKFIELD_01_09_2021__padrao_2__03780401000108__31122020__dcc16cbc.xlsx
│       │   ├── BROOKFILD 04_05_2022__66817274.xlsx
│       │   ├── BROOKFILD 04_05_2022__padrao_2__03780401000108__31122021__66817274.xlsx
│       │   ├── BTG 01102024__bd2b7877.xlsx
│       │   ├── BTG 01102024__padrao_3__30306294000226__31122023__bd2b7877.xlsx
│       │   ├── BTG 15102025__e7ed4dfc.xlsx
│       │   ├── BTG 15102025__padrao_3__07133522000100__31122024__e7ed4dfc.xlsx
│       │   ├── BTG PACTUAL (BANCO)_08-11_2021__60693ecb.xlsx
│       │   ├── BTG_05092023__fa59a299.xlsx
│       │   ├── BTG_05092023__padrao_3__30306294000145__31122022__fa59a299.xlsx
│       │   ├── BTG_29.07.2024__8ddb7a31.xlsx
│       │   ├── BTG_29.07.2024__padrao_3__48400908000119__31122023__8ddb7a31.xlsx
│       │   ├── CANADIAN 08062026__2aac8fb2.xlsx
│       │   ├── CANADIAN 08062026__padrao_6__26215280000149__31122025__2aac8fb2.xlsx
│       │   ├── CANADIAN RARTING 26022026__58f29677.xlsx
│       │   ├── CANADIAN RATING 21012026__6b90af6a.xlsx
│       │   ├── CANADIAN RATING 21012026__padrao_6__17302990000115__31122024__6b90af6a.xlsx
│       │   ├── CANADIAN SOLAR_06_10_2022__e5ffa9cd.xlsx
│       │   ├── CANADIAN_17042023__66c9d8cf.xlsx
│       │   ├── CAPITALE 01102025__b6c7145e.xlsx
│       │   ├── CAPITALE 01102025__padrao_3__11599292000147__31122024__b6c7145e.xlsx
│       │   ├── CAPITALE 27032026__52069d58.xlsx
│       │   ├── CAPITALE 27032026__padrao_6__11599292000147__31122024__52069d58.xlsx
│       │   ├── CAPITALE 28052026__cea1dd9e.xlsx
│       │   ├── CAPITALE 28052026__padrao_6__11599292000147__31122025__cea1dd9e.xlsx
│       │   ├── CAPITALE 30_05_2022__8191a942.xlsx
│       │   ├── CAPITALE 30_05_2022__padrao_2__11599292000147__31122021__8191a942.xlsx
│       │   ├── CAPITALE_16062023__6c9f544e.xlsx
│       │   ├── CAPITALE_16062023__padrao_3__11599292000147__31122022__6c9f544e.xlsx
│       │   ├── CAPITALE_26.06.2024__20236dcb.xlsx
│       │   ├── CAPITALE_26.06.2024__padrao_6__11599292000147__31122023__20236dcb.xlsx
│       │   ├── CASA DOS VENTOS 03 05 2024__f6e5bda8.xlsx
│       │   ├── CASA DOS VENTOS 03 05 2024__padrao_3__33933760000100__31122023__f6e5bda8.xlsx
│       │   ├── CASA DOS VENTOS 08_06_2022__f87323ec.xlsx
│       │   ├── CASA DOS VENTOS 08_06_2022__padrao_2__33933760000100__31122021__f87323ec.xlsx
│       │   ├── CASA DOS VENTOS 30072026__b7880a13.xlsx
│       │   ├── CASA DOS VENTOS 30072026__padrao_6__33933760000100__31122025__b7880a13.xlsx
│       │   ├── CASA DOS VENTOS RATING 29102025__1d82f6e7.xlsx
│       │   ├── CASA DOS VENTOS RATING 29102025__padrao_7__33933760000100__31122024__1d82f6e7.xlsx
│       │   ├── CASA_DOS_VENTOS_11082023__5f6a7839.xlsx
│       │   ├── CASA_DOS_VENTOS_11082023__padrao_3__33933760000100__31122022__5f6a7839.xlsx
│       │   ├── CASTROLANDA 01042024__50e10cc9.xlsx
│       │   ├── CASTROLANDA 01042024__padrao_3__76108349003200__31122023__50e10cc9.xlsx
│       │   ├── CASTROLANDA 10122025__04318565.xlsx
│       │   ├── CASTROLANDA 10122025__padrao_6__76108349003200__31122024__04318565.xlsx
│       │   ├── CDV_SIMULACAO__d6897ea1.xlsx
│       │   ├── CDVSA 12082026__c5a7c7af.xlsx
│       │   ├── CEEE 14042026__b26e5045.xlsx
│       │   ├── CEEE 14042026__padrao_6__39881421000104__31122024__b26e5045.xlsx
│       │   ├── CEESAM 23072026__38be06ee.xlsx
│       │   ├── CEI 10092025__42d1536b.xlsx
│       │   ├── CEI 10092025__padrao_3__32234363000188__31122024__42d1536b.xlsx
│       │   ├── CEI COMERCIALIZADORA 17082026__a0f84bb7.xlsx
│       │   ├── CEI COMERCIALIZADORA 17082026__padrao_6__32234363000188__31122025__a0f84bb7.xlsx
│       │   ├── CEI ENERGETICA 17082026__97243686.xlsx
│       │   ├── CEI ENERGETICA 17082026__padrao_6__32234363000188__31122024__97243686.xlsx
│       │   ├── CELESC 11_05_2022__394a24ec.xlsx
│       │   ├── CELESC 11_05_2022__padrao_2__03953509000147__31122021__394a24ec.xlsx
│       │   ├── CELESC Geração 28052026__0076c014.xlsx
│       │   ├── CELESC Geração 28052026__padrao_6__08336804000178__31122025__0076c014.xlsx
│       │   ├── CELESC_16042024__f55e254f.xlsx
│       │   ├── CELESC_16042024__padrao_3__04149295000113__31122023__f55e254f.xlsx
│       │   ├── CEMIG 05-07-2024 trading__e24e2119.xlsx
│       │   ├── CEMIG 05-07-2024 trading__padrao_3__05263973000137__31122023__e24e2119.xlsx
│       │   ├── CEMIG H COMERCIALIZAÇÃO_23_02_2022__7a8bea28.xlsx
│       │   ├── CEMIG_09062023__a2e0b5ed.xlsx
│       │   ├── CEMIG_09062023__padrao_3__17155730000164__31122022__a2e0b5ed.xlsx
│       │   ├── CEMIG_13.06.2024__37922637.xlsx
│       │   ├── CEMIG_13.06.2024__padrao_3__17155730000164__31122023__37922637.xlsx
│       │   ├── CEMIG_24092025__76ed85dc.xlsx
│       │   ├── CEMIG_24092025__padrao_3__17155730000164__03092025__76ed85dc.xlsx
│       │   ├── CENTRAL 06_05_2022__62e72943.xlsx
│       │   ├── CENTRAL 06_05_2022__padrao_2__30983948000175__31122021__62e72943.xlsx
│       │   ├── CENTRAL 08 05 2024__3265f642.xlsx
│       │   ├── CENTRAL 08 05 2024__padrao_6__30983948000175__31122023__3265f642.xlsx
│       │   ├── Central_22_05_2025__ffe4a8fd.xlsx
│       │   ├── Central_22_05_2025__padrao_3__30983948000175__31122024__ffe4a8fd.xlsx
│       │   ├── CERCAR SA RATING 12022026__db7b89df.xlsx
│       │   ├── CERCAR SA RATING 12022026__padrao_6__76879295000180__31122024__db7b89df.xlsx
│       │   ├── CGN 05122025__94044130.xlsx
│       │   ├── CGN 05122025__padrao_6__48563988000123__31122024__94044130.xlsx
│       │   ├── CGN Brasil 11082026__564ed557.xlsx
│       │   ├── CGN Brasil 11082026__padrao_6__48563988000123__31122025__564ed557.xlsx
│       │   ├── CGN_30.07.2024__7ef814a5.xlsx
│       │   ├── CGN_30.07.2024__padrao_3__48563988000123__31122023__7ef814a5.xlsx
│       │   ├── CGN_30102023__63914819.xlsx
│       │   ├── CGN_30102023__padrao_3__48563988000123__31122022__63914819.xlsx
│       │   ├── COMEL 18062025__51265a1d.xlsx
│       │   ├── COMEL 18062025__padrao_3__39953546000100__31122024__51265a1d.xlsx
│       │   ├── COMEL_2023__c4e1ec85.xlsx
│       │   ├── COMEL_2023__padrao_3__39953546000100__31122023__c4e1ec85.xlsx
│       │   ├── COMERC 13_06_2022__66afcfeb.xlsx
│       │   ├── COMERC 13_06_2022__padrao_2__58177643000195__31122021__66afcfeb.xlsx
│       │   ├── COMERC 29 04 2024__38814998.xlsx
│       │   ├── COMERC 29 04 2024__padrao_3__25369840000157__31122023__38814998.xlsx
│       │   ├── COMERC PART 23072026__9742e0b4.xlsx
│       │   ├── COMERC PART 23072026__padrao_6__25369840000157__31122025__9742e0b4.xlsx
│       │   ├── COMERC Participações 28112023__15650f7c.xlsx
│       │   ├── COMERC Participações 28112023__padrao_3__25369840000157__31122022__15650f7c.xlsx
│       │   ├── COMERC_19062023__a1a6e8ff.xlsx
│       │   ├── COMERC_19062023__padrao_3__58177643000195__31122022__a1a6e8ff.xlsx
│       │   ├── CONVEX 18082026__20d607fd.xlsx
│       │   ├── CONVEX 18082026__padrao_6__27184790000169__31122025__20d607fd.xlsx
│       │   ├── COPEL_23.07.2024__7a3ea1a7.xlsx
│       │   ├── COPEL_23.07.2024__padrao_3__19125927000186__31122023__7a3ea1a7.xlsx
│       │   ├── COPELCOM_16_04_2021__a394155f.xlsx
│       │   ├── COPELCOM_16_04_2021__padrao_2__19125927000186__31122020__a394155f.xlsx
│       │   ├── COPELGET_27112024__4b9379fb.xlsx
│       │   ├── COPELGET_27112024__padrao_3__04370282000170__31122023__4b9379fb.xlsx
│       │   ├── COPPREL 16062026__4219c92b.xlsx
│       │   ├── COPPREL 16062026__padrao_6__42102025000146__31122025__4219c92b.xlsx
│       │   ├── COPREL GERAÇÃO 23062026__fc3e160e.xlsx
│       │   ├── COPREL GERAÇÃO 23062026__padrao_6__08323274000123__31122025__fc3e160e.xlsx
│       │   ├── COTESA 30_05_2022__5f70d8ba.xlsx
│       │   ├── COTESA 30_05_2022__padrao_2__85235430000145__31122021__5f70d8ba.xlsx
│       │   ├── COTESA_14_10_2021__c6c551ed.xlsx
│       │   ├── COTESA_14_10_2021__padrao_2__85235430000145__31122020__c6c551ed.xlsx
│       │   ├── CPFL 04072025__1__c60754b4.xlsx
│       │   ├── CPFL 04072025__1__padrao_3__04973790000142__31122024__c60754b4.xlsx
│       │   ├── CPFL 04072025__5d728606.xlsx
│       │   ├── CPFL 04072025__padrao_3__08439659000150__31122024__5d728606.xlsx
│       │   ├── CPFL 06082026__9d30dc0c.xlsx
│       │   ├── CPFL 06082026__padrao_6__04973790000142__22012026__9d30dc0c.xlsx
│       │   ├── CPFL_01_06_2022__ee7a5bd0.xlsx
│       │   ├── CPFL_11.08.2023___b061dcba.xlsx
│       │   ├── CPFL_11.08.2023___padrao_3__04973790000142__31122022__b061dcba.xlsx
│       │   ├── CPFL_28.08.2024__c8829980.xlsx
│       │   ├── CPFL_28.08.2024__padrao_3__04973790000142__31122023__c8829980.xlsx
│       │   ├── CTG 24092025__78460486.xlsx
│       │   ├── CTG 24092025__padrao_3__14295008000137__21032025__78460486.xlsx
│       │   ├── CTG BRNE_28.08.2024__7a62e419.xlsx
│       │   ├── CTG BRNE_28.08.2024__padrao_3__14295008000137__31122023__7a62e419.xlsx
│       │   ├── CTG NE 02022024__6aa1614e.xlsx
│       │   ├── CTG NE 02022024__padrao_3__14295008000137__31122022__6aa1614e.xlsx
│       │   ├── CTG Trading_04_06_2021__c9586425.xlsx
│       │   ├── CTG Trading_04_06_2021__padrao_2__03631957000124__31122020__c9586425.xlsx
│       │   ├── CTG Trading_16082023__fa6ef875.xlsx
│       │   ├── CTG Trading_16082023__padrao_3__03631957000124__31122022__fa6ef875.xlsx
│       │   ├── CTG trading_28.08.2024__d727535f.xlsx
│       │   ├── CTG trading_28.08.2024__padrao_3__03631957000124__31122023__d727535f.xlsx
│       │   ├── CTGBRNE 10042026__e84a60a7.xlsx
│       │   ├── CTGBRNE 10042026__padrao_6__14295008000137__31122024__e84a60a7.xlsx
│       │   ├── CTGNE 23072026__c99e458d.xlsx
│       │   ├── CTGNE 23072026__padrao_6__14295008000137__31122025__c99e458d.xlsx
│       │   ├── CZARNIKOW 09062026__46500a1c.xlsx
│       │   ├── CZARNIKOW 09062026__padrao_6__07794616000120__31122025__46500a1c.xlsx
│       │   ├── CZARNIKOW 13062025__4bb069a4.xlsx
│       │   ├── CZARNIKOW 13062025__padrao_3__07794616000120__31122024__4bb069a4.xlsx
│       │   ├── Czarnikow 27-01-2025__2cf2e811.xlsx
│       │   ├── Czarnikow 27-01-2025__padrao_3__07794616000120__31122023__2cf2e811.xlsx
│       │   ├── CZARNIKOW 27032026__c6d78952.xlsx
│       │   ├── CZARNIKOW 27032026__padrao_6__07794616000120__31122024__c6d78952.xlsx
│       │   ├── CZARNIKOW 27_09_2022__4276080a.xlsx
│       │   ├── CZARNIKOW 27_09_2022__padrao_2__07794616000120__31122021__4276080a.xlsx
│       │   ├── CZARNIKOW_07_06_2021 (zerada manualmente__177ea59e.xlsx
│       │   ├── CZARNIKOW_07_06_2021 (zerada manualmente__padrao_2__07794616000120__31122020__177ea59e.xlsx
│       │   ├── D3 Comercializadora_18.03.2024__f8b9b1a3.xlsx
│       │   ├── D3 Comercializadora_18.03.2024__padrao_6__45836050000141__31122023__f8b9b1a3.xlsx
│       │   ├── DANSKE 10072025__f6af2052.xlsx
│       │   ├── DANSKE 10072025__padrao_3__40382949000118__31122024__f6af2052.xlsx
│       │   ├── DANSKE 12112024__09f12f88.xlsx
│       │   ├── DANSKE 12112024__padrao_6__40382949000118__31122023__09f12f88.xlsx
│       │   ├── DANSKE 27032026__90e63584.xlsx
│       │   ├── DANSKE 27032026__padrao_6__40382949000118__31122024__90e63584.xlsx
│       │   ├── DANSKE 30072026__71de7011.xlsx
│       │   ├── DANSKE 30072026__padrao_6__40382949000118__31122025__71de7011.xlsx
│       │   ├── DEAL 10_05_2022__da502dae.xlsx
│       │   ├── DEAL 10_05_2022__padrao_2__10671322000116__31122021__da502dae.xlsx
│       │   ├── DEAL 16102025__4def4933.xlsx
│       │   ├── DEAL 16102025__padrao_3__10671322000116__31122024__4def4933.xlsx
│       │   ├── DEAL 27102023__b7d51c48.xlsx
│       │   ├── DEAL 27102023__padrao_3__10671322000116__31122022__b7d51c48.xlsx
│       │   ├── DEAL 29062026__c9817d83.xlsx
│       │   ├── DEAL 29062026__padrao_6__10671322000116__31122025__c9817d83.xlsx
│       │   ├── DEAL RATING 16102025__14abab02.xlsx
│       │   ├── DEAL RATING 16102025__padrao_6__10671322000116__31122024__14abab02.xlsx
│       │   ├── DEAL_14_10_2021__6402fbfb.xlsx
│       │   ├── DEAL_14_10_2021__padrao_2__10671322000116__31122020__6402fbfb.xlsx
│       │   ├── DEAL_26.06.2024__62098ec6.xlsx
│       │   ├── DEAL_26.06.2024__padrao_6__10671322000116__31122023__62098ec6.xlsx
│       │   ├── DELTA 12_04_2022 31 12 2021__e2ea8941.xlsx
│       │   ├── DELTA 12_04_2022 31 12 2021__padrao_2__04802543000183__31122020__e2ea8941.xlsx
│       │   ├── Delta Energia 01072025__d327c819.xlsx
│       │   ├── DELTA_19022025__8bba3871.xlsx
│       │   ├── DELTA_19022025__padrao_3__04802543000183__31122023__8bba3871.xlsx
│       │   ├── DESTTRA_02_09_2021__f852d5fa.xlsx
│       │   ├── DESTTRA_02_09_2021__padrao_2__30124679000191__31122020__f852d5fa.xlsx
│       │   ├── DIFERENCIAL 13_04_2022__c8314860.xlsx
│       │   ├── DIFERENCIAL 13_04_2022__padrao_2__07393256000155__31122021__c8314860.xlsx
│       │   ├── DIFERENCIAL_02_09_2021__fe547de6.xlsx
│       │   ├── DIFERENCIAL_02_09_2021__padrao_2__07393256000155__31122020__fe547de6.xlsx
│       │   ├── DIFERENCIAL_16.05.2024__baf2fadb.xlsx
│       │   ├── DIFERENCIAL_16.05.2024__padrao_3__07393256000155__31122023__baf2fadb.xlsx
│       │   ├── DIFERENCIAL_20072023__46536b7a.xlsx
│       │   ├── DIFERENCIAL_20072023__padrao_3__07393256000155__31122022__46536b7a.xlsx
│       │   ├── ECEL - ELETRON_03_09_2021__db966111.xlsx
│       │   ├── ECEL - ELETRON_03_09_2021__padrao_2__15087610000141__31122020__db966111.xlsx
│       │   ├── ECHOENERGIA 30062026__dace17c6.xlsx
│       │   ├── ECHOENERGIA 30062026__padrao_6__31932088000103__31122024__dace17c6.xlsx
│       │   ├── Echoenergia Participações__a4c31967.xlsx
│       │   ├── Echoenergia Participações__padrao_2__31932088000103__31122020__a4c31967.xlsx
│       │   ├── ECHOENERGIA_09_09_2021__bcb4c850.xlsx
│       │   ├── ECHOENERGIA_09_09_2021__padrao_2__24743678000122__31122020__bcb4c850.xlsx
│       │   ├── ECOM 17_05_2022__3476990c.xlsx
│       │   ├── ECOM 17_05_2022__padrao_2__05352237000155__31122021__3476990c.xlsx
│       │   ├── ECOM 22042026__2c05bea0.xlsx
│       │   ├── ECOM 22042026__padrao_6__05352237000155__31122025__2c05bea0.xlsx
│       │   ├── ECOM 23112023__8d44f2fe.xlsx
│       │   ├── ECOM 23112023__padrao_6__05352237000155__31122022__8d44f2fe.xlsx
│       │   ├── ECOM 27032026__4c9e4ba9.xlsx
│       │   ├── ECOM 27032026__padrao_6__05352237000155__31122024__4c9e4ba9.xlsx
│       │   ├── ECOM_11042024__b0f37e54.xlsx
│       │   ├── ECOM_11042024__padrao_3__05352237000155__31122023__b0f37e54.xlsx
│       │   ├── ECOM_14_10_2021__f20d442d.xlsx
│       │   ├── ECOM_14_10_2021__padrao_2__05352237000155__31122020__f20d442d.xlsx
│       │   ├── ECOM_2024__d2ac0d64.xlsx
│       │   ├── ECOM_2024__padrao_3__05352237000155__31122024__d2ac0d64.xlsx
│       │   ├── EDF 01042026__941a581f.xlsx
│       │   ├── EDF 01042026__padrao_6__21812954000179__31122024__941a581f.xlsx
│       │   ├── EDF 06122023__75471526.xlsx
│       │   ├── EDF 06122023__padrao_3__35984409000174__31122022__75471526.xlsx
│       │   ├── EDF 30062026__c600a90d.xlsx
│       │   ├── EDF 30062026__padrao_6__35984409000174__31122024__c600a90d.xlsx
│       │   ├── EDF RENEWABLES VERDECOM 03082026__069474e9.xlsx
│       │   ├── EDF RENEWABLES VERDECOM 03082026__padrao_6__35984409000174__31122025__069474e9.xlsx
│       │   ├── EDF VERDECOM 22082025__394d6295.xlsx
│       │   ├── EDF VERDECOM 22082025__padrao_3__35984409000174__31122024__394d6295.xlsx
│       │   ├── EDP 21052026__772dd5a8.xlsx
│       │   ├── EDP 21052026__padrao_6__04149295000113__31122025__772dd5a8.xlsx
│       │   ├── EDP_12062023__3fd84da0.xlsx
│       │   ├── EDP_12062023__padrao_3__04149295000113__31122022__3fd84da0.xlsx
│       │   ├── EDP_2025__b45c24de.xlsx
│       │   ├── EDP_2025__padrao_3__04149295000113__31122024__b45c24de.xlsx
│       │   ├── EEI BARIGUI_04_02_2022 divididos por 12__ae974cff.xlsx
│       │   ├── EEI BARIGUI_04_02_2022 divididos por 12__padrao_2__29993083000149__31122021__ae974cff.xlsx
│       │   ├── EGS_29_08_2024__4d3964b7.xlsx
│       │   ├── EGS_29_08_2024__padrao_3__52177777000120__31122023__4d3964b7.xlsx
│       │   ├── EKOA 06_06_2022__4b56f384.xlsx
│       │   ├── EKOA 06_06_2022__padrao_2__28640358000106__31122021__4b56f384.xlsx
│       │   ├── EKOA_03_09_2021__63566cb7.xlsx
│       │   ├── EKOA_03_09_2021__padrao_2__28640358000106__31122020__63566cb7.xlsx
│       │   ├── ELECTRA 26032024__4ff8c117.xlsx
│       │   ├── ELECTRA 26032024__padrao_3__04518259000180__30062023__4ff8c117.xlsx
│       │   ├── ELECTRA 29_08_2022__0e2c4687.xlsx
│       │   ├── ELECTRA 29_08_2022__padrao_2__04518259000180__31122021__0e2c4687.xlsx
│       │   ├── ELECTRA ENERGY 18_04_2023__c07f212e.xlsx
│       │   ├── ELECTRA ENERGY 18_04_2023__padrao_3__04518259000180__31122022__c07f212e.xlsx
│       │   ├── ELECTRA ENERGY_2024__bd4943f3.xlsx
│       │   ├── ELECTRA ENERGY_2024__padrao_3__04518259000180__31122024__bd4943f3.xlsx
│       │   ├── ELECTRA_02_09_2021__29638a1c.xlsx
│       │   ├── ELECTRA_02_09_2021__padrao_2__04518259000180__31122020__29638a1c.xlsx
│       │   ├── ELECTRA_15042024__a6daf950.xlsx
│       │   ├── ELECTRA_15042024__padrao_3__04518259000180__31122023__a6daf950.xlsx
│       │   ├── ELERA COM 31072025__6a6127b8.xlsx
│       │   ├── ELERA COM 31072025__padrao_3__03780401000108__31122024__6a6127b8.xlsx
│       │   ├── ELERA_19012024__74a614b1.xlsx
│       │   ├── ELERA_19012024__padrao_3__03780401000108__31122022__74a614b1.xlsx
│       │   ├── ELERA_30.07.2024__f7891b81.xlsx
│       │   ├── ELERA_30.07.2024__padrao_3__03780401000108__31122023__f7891b81.xlsx
│       │   ├── ELETROBRAS_24092025__169c22c5.xlsx
│       │   ├── ELETROBRAS_24092025__padrao_3__00001180000126__31122024__169c22c5.xlsx
│       │   ├── ELETROBRAS__f4f5ddb1.xlsx
│       │   ├── ELETROBRAS__padrao_3__00001180000207__31122024__f4f5ddb1.xlsx
│       │   ├── ELETRON 30_05_2022__90074bfa.xlsx
│       │   ├── ELETRON 30_05_2022__padrao_2__15087610000141__31122021__90074bfa.xlsx
│       │   ├── ENECEL_03_09_2021__d4374007.xlsx
│       │   ├── ENECEL_03_09_2021__padrao_2__25466251000197__31122020__d4374007.xlsx
│       │   ├── ENECEL_26.06.2024__09a6c61b.xlsx
│       │   ├── ENECEL_26.06.2024__padrao_3__25466251000197__31122023__09a6c61b.xlsx
│       │   ├── ENEL 22_06_2022__845e6401.xlsx
│       │   ├── Enel Brasil_25092025__bff44514.xlsx
│       │   ├── Enel Brasil_25092025__padrao_3__30248458000125__27082024__bff44514.xlsx
│       │   ├── ENEL TRADING 27112023__8b8f99c4.xlsx
│       │   ├── ENEL TRADING 27112023__padrao_3__30248458000125__31122022__8b8f99c4.xlsx
│       │   ├── ENEL_29.07.2024__d0ee4997.xlsx
│       │   ├── ENEL_29.07.2024__padrao_3__30248458000125__31122023__d0ee4997.xlsx
│       │   ├── ENERCORE 01072026__6e4eb1d8.xlsx
│       │   ├── ENERCORE 01072026__padrao_6__18416364000112__31122025__6e4eb1d8.xlsx
│       │   ├── ENERCORE 07_04_2022__0499e125.xlsx
│       │   ├── ENERCORE 07_04_2022__padrao_2__18416364000112__31122021__0499e125.xlsx
│       │   ├── ENERCORE_11042024__a29d0755.xlsx
│       │   ├── ENERCORE_11042024__padrao_3__18416364000112__31122023__a29d0755.xlsx
│       │   ├── ENERCORE_2024__2bbf75e0.xlsx
│       │   ├── ENERCORE_2024__padrao_3__18416364000112__31122024__2bbf75e0.xlsx
│       │   ├── ENERCORE_22032023__e26580ab.xlsx
│       │   ├── ENERCORE_22032023__padrao_3__18416364000112__31122022__e26580ab.xlsx
│       │   ├── ENERGEST 17082026__d6c4b48e.xlsx
│       │   ├── ENERGEST 17082026__padrao_6__04029601000188__31122025__d6c4b48e.xlsx
│       │   ├── ENERGETICA 03_03_2022__3f7a2d5e.xlsx
│       │   ├── ENERGETICA 03_03_2022__padrao_2__20978264000121__31122021__3f7a2d5e.xlsx
│       │   ├── ENERGISA 07052024__3e786d54.xlsx
│       │   ├── ENERGISA 07052024__padrao_3__07685694000197__31122023__3e786d54.xlsx
│       │   ├── ENERGISA 08052026__1bebb2db.xlsx
│       │   ├── ENERGISA 08052026__padrao_6__07685694000197__31122025__1bebb2db.xlsx
│       │   ├── ENERGISA 30102025__dacbf519.xlsx
│       │   ├── ENERGISA 30102025__padrao_7__07685694000197__31122024__dacbf519.xlsx
│       │   ├── ENERGISA(GRUPO)_04_09_2021__1ae7d23e.xlsx
│       │   ├── ENERGIZOU 17_03_2022__5271a610.xlsx
│       │   ├── ENERGIZOU 17_03_2022__padrao_2__30693787000185__31122021__5271a610.xlsx
│       │   ├── ENERGIZOU_05.06.2024__12c7f73e.xlsx
│       │   ├── ENERGIZOU_05.06.2024__padrao_6__30693787000185__31122023__12c7f73e.xlsx
│       │   ├── ENERPEIXE 20082026__14cea463.xlsx
│       │   ├── ENERPEIXE 20082026__padrao_6__04426411000102__31122025__14cea463.xlsx
│       │   ├── ENERPEIXE COMERCIALIZADORA16092025__d4e76877.xlsx
│       │   ├── ENERPEIXE COMERCIALIZADORA16092025__padrao_3__04426411000102__31122024__d4e76877.xlsx
│       │   ├── ENEVA 28072026__9b2a45e2.xlsx
│       │   ├── ENEVA 28072026__padrao_6__04423567000121__31122025__9b2a45e2.xlsx
│       │   ├── ENEVA 30102025__9c316a99.xlsx
│       │   ├── ENEVA 30102025__padrao_7__04423567000121__31122024__9c316a99.xlsx
│       │   ├── ENEVA_05042023__00ffa1cf.xlsx
│       │   ├── ENEVA_05_04_2022__559d7337.xlsx
│       │   ├── ENEVA_29.05.2024__1__e654b06c.xlsx
│       │   ├── ENEVA_29.05.2024__1__padrao_3__09185485000100__31122023__e654b06c.xlsx
│       │   ├── ENEVA_29.05.2024__aa25fd1d.xlsx
│       │   ├── ENEVA_29.05.2024__padrao_3__04423567000121__31122023__aa25fd1d.xlsx
│       │   ├── ENEX_17_06_2021__f4452e93.xlsx
│       │   ├── ENEX_17_06_2021__padrao_2__12458962000178__31122020__f4452e93.xlsx
│       │   ├── ENGEFORM 25062026__9f93cf8c.xlsx
│       │   ├── ENGEFORM 25062026__padrao_6__42311687000126__31122025__9f93cf8c.xlsx
│       │   ├── ENGIE 01072025__bbd16987.xlsx
│       │   ├── ENGIE 01072025__padrao_3__04100556000100__31122024__bbd16987.xlsx
│       │   ├── ENGIE 12052026__e8ed31fe.xlsx
│       │   ├── ENGIE 12052026__padrao_6__04100556000100__31122025__e8ed31fe.xlsx
│       │   ├── ENGIE COM (GRUPO)_06_10_2021__20285b26.xlsx
│       │   ├── ENGIE TRADING_(GRUPO)_18_10_2021__ce1d26f6.xlsx
│       │   ├── ENGIE_06.06.2024__a39d1402.xlsx
│       │   ├── ENGIE_06.06.2024__padrao_3__31635668000139__31122023__a39d1402.xlsx
│       │   ├── Engie_31082023__1597818f.xlsx
│       │   ├── Engie_31082023__padrao_3__04100556000100__31122022__1597818f.xlsx
│       │   ├── ENGIECOM_06.06.2024__c0b8a668.xlsx
│       │   ├── ENGIECOM_06.06.2024__padrao_3__04100556000100__31122023__c0b8a668.xlsx
│       │   ├── EngieTrading_05092023__ac04612c.xlsx
│       │   ├── EngieTrading_05092023__padrao_3__31635668000139__31122022__ac04612c.xlsx
│       │   ├── EQUATORIAL (ECHO)_25092025__19c71b7a.xlsx
│       │   ├── EQUATORIAL (ECHO)_25092025__padrao_3__31932088000103__31122024__19c71b7a.xlsx
│       │   ├── EQUATORIAL RENOVAVEIS 08062026__f95deffa.xlsx
│       │   ├── EQUATORIAL RENOVAVEIS 08062026__padrao_6__31932088000103__31122024__f95deffa.xlsx
│       │   ├── ESFERA 02_08_2022__b19f3b41.xlsx
│       │   ├── ESFERA 02_08_2022__padrao_2__26940979000171__31122021__b19f3b41.xlsx
│       │   ├── ESFERA 26 04 2024__7cc6090c.xlsx
│       │   ├── ESFERA 26 04 2024__padrao_6__26940979000171__31122023__7cc6090c.xlsx
│       │   ├── ESFERA 27022024__1382b4b3.xlsx
│       │   ├── ESFERA 27022024__padrao_6__26940979000171__31122022__1382b4b3.xlsx
│       │   ├── EVEREST 06_05_2022__c03f7892.xlsx
│       │   ├── EVEREST 06_05_2022__padrao_2__21256386000177__31122021__c03f7892.xlsx
│       │   ├── EVEREST_03_09_2021__63dabfbe.xlsx
│       │   ├── EVEREST_03_09_2021__padrao_2__21256386000177__31122020__63dabfbe.xlsx
│       │   ├── EVO 20112023__e5615262.xlsx
│       │   ├── EVO 20112023__padrao_6__30902608000172__31122022__e5615262.xlsx
│       │   ├── EVO ENERGIA 27062025__acb39ff5.xlsx
│       │   ├── EVO ENERGIA 27062025__padrao_3__30902608000172__31122024__acb39ff5.xlsx
│       │   ├── EVO ENERGIA 30_05_2022__6d923749.xlsx
│       │   ├── EVO ENERGIA 30_05_2022__padrao_2__30902608000172__31122021__6d923749.xlsx
│       │   ├── EVO ENERGIA _25_05_2021__67ecc47c.xlsx
│       │   ├── EVO ENERGIA _25_05_2021__padrao_2__30902608000172__31122020__67ecc47c.xlsx
│       │   ├── EVO_20.05.2024__856baeb1.xlsx
│       │   ├── EVO_20.05.2024__padrao_6__30902608000172__31122023__856baeb1.xlsx
│       │   ├── EVOLUTION_19_03_2021__c82b864f.xlsx
│       │   ├── EVOLUTION_19_03_2021__padrao_2__31897236000104__31122020__c82b864f.xlsx
│       │   ├── EXATA_03_09_2021__2dfdc41d.xlsx
│       │   ├── EXATA_03_09_2021__padrao_2__33931753000170__31122020__2dfdc41d.xlsx
│       │   ├── EXPONENCIAL 01112024__73abf9fe.xlsx
│       │   ├── EXPONENCIAL 01112024__padrao_3__26914969000161__31122023__73abf9fe.xlsx
│       │   ├── EXPONENCIAL 10_03_2022__17293803.xlsx
│       │   ├── EXPONENCIAL 10_03_2022__padrao_2__26914969000161__31122021__17293803.xlsx
│       │   ├── FIBRA 06082026__484f0112.xlsx
│       │   ├── FIBRA 06082026__padrao_6__08578334000159__31122025__484f0112.xlsx
│       │   ├── Fibra Energy 14052025__a982b556.xlsx
│       │   ├── Fibra Energy 14052025__padrao_3__08578334000159__31122024__a982b556.xlsx
│       │   ├── Fibra_2024__5ebc10fc.xlsx
│       │   ├── FIBRA_GRUPO 24062025__2cd524ae.xlsx
│       │   ├── FIBRA_GRUPO 24062025__padrao_3__08578334000159__31122024__2cd524ae.xlsx
│       │   ├── FICHA AMERICA_18.06.2023__d8167276.xlsx
│       │   ├── FICHA ARGON_16.06.2023__42c92bc5.xlsx
│       │   ├── FICHA ARGON_16.06.2023__padrao_3__21642355000154__31122022__42c92bc5.xlsx
│       │   ├── FICHA BOVEN_16.06.2023__9f48f084.xlsx
│       │   ├── FICHA BOVEN_16.06.2023__padrao_3__14609649000119__31122022__9f48f084.xlsx
│       │   ├── FICHA EXPONENCIAL_16.06.2023__2fc69327.xlsx
│       │   ├── FICHA EXPONENCIAL_16.06.2023__padrao_3__26914969000161__31122022__2fc69327.xlsx
│       │   ├── FICHA GOLD_19.06.2023__bbe25404.xlsx
│       │   ├── FICHA GOLD_19.06.2023__padrao_3__30483222000173__31122022__bbe25404.xlsx
│       │   ├── FICHA MODELO_xx.xx.2024__ad29fd5d.xlsx
│       │   ├── FICHA MODELO_xx.xx.2024__padrao_6__17386017000121__31122023__ad29fd5d.xlsx
│       │   ├── FICHA MODELO_xx.xx.2025_1.0__8886fe30.xlsx
│       │   ├── FICHA MODELO_xx.xx.2025_1.0__padrao_3__04023261000188__31122023__8886fe30.xlsx
│       │   ├── FICHA MODELO_xx.xx.xxxx__29bf6542.xlsx
│       │   ├── FICHA MODELO_xx.xx.xxxx__4__d068688a.xlsx
│       │   ├── FICHA MODELO_xx.xx.xxxx__4__padrao_6__28397998000129__31122023__d068688a.xlsx
│       │   ├── FICHA MODELO_xx.xx.xxxx__padrao_6__28397998000129__31122022__29bf6542.xlsx
│       │   ├── Ficha Padrão Backup__84ab0b64.xlsx
│       │   ├── Ficha Padrão__de714f70.xlsx
│       │   ├── FICHA URCA_20.06.2023__e5ecf41d.xlsx
│       │   ├── FICHA URCA_20.06.2023__padrao_3__32185360000100__31122022__e5ecf41d.xlsx
│       │   ├── FICHA_GERADORAS_LAJARI_PASSO4__818c2dd7.xlsx
│       │   ├── FICHA_GERADORAS_LAJARI_PASSO4__padrao_6__09020211000160__31122025__818c2dd7.xlsx
│       │   ├── FLASH 11072025__83422c0d.xlsx
│       │   ├── FLASH 11072025__padrao_3__30834939000112__31122024__83422c0d.xlsx
│       │   ├── FLASH ENERGY 25042024__86deb931.xlsx
│       │   ├── FLASH ENERGY 25042024__padrao_6__30834939000112__31122023__86deb931.xlsx
│       │   ├── FLOW_03_09_2021__802ee549.xlsx
│       │   ├── FLOW_03_09_2021__padrao_2__30840548000100__31122021__802ee549.xlsx
│       │   ├── FOCUS ENERGIA _07_05_2021__e3afbdf5.xlsx
│       │   ├── FOCUS ENERGIA _07_05_2021__padrao_2__07760179000124__31122020__e3afbdf5.xlsx
│       │   ├── FOTOVO 01_09_2022__6a2f6e4e.xlsx
│       │   ├── FOTOVO 01_09_2022__padrao_2__27483435000190__31122021__6a2f6e4e.xlsx
│       │   ├── FOTOVO 30-04-2026__a90c23b1.xlsx
│       │   ├── FOTOVO 30-04-2026__padrao_6__27483435000190__31122024__a90c23b1.xlsx
│       │   ├── FOTOVO_11.08.2023___eb6cbd02.xlsx
│       │   ├── FOTOVO_11.08.2023___padrao_4__27483435000190__31122022__eb6cbd02.xlsx
│       │   ├── FOTOVO_21.05.2024__a3de2533.xlsx
│       │   ├── FOTOVO_21.05.2024__padrao_6__27483435000190__31122023__a3de2533.xlsx
│       │   ├── Foz do Chapeco 05082026__23f7d636.xlsx
│       │   ├── Foz do Chapeco 05082026__padrao_6__04591168000170__31122025__23f7d636.xlsx
│       │   ├── FOZ DO CHAPECO RATING 27012026__0852ea15.xlsx
│       │   ├── FOZ DO CHAPECO RATING 27012026__padrao_6__07829836000142__31122024__0852ea15.xlsx
│       │   ├── GALAPAGOS 30102025__6044d919.xlsx
│       │   ├── GALP 11122023__084ec7f7.xlsx
│       │   ├── GALP 11122023__padrao_6__16974249000138__31122022__084ec7f7.xlsx
│       │   ├── GALP 25112024__f2117de9.xlsx
│       │   ├── GALP 25112024__padrao_6__16974249000138__31122023__f2117de9.xlsx
│       │   ├── GALP 27082025__c75d513f.xlsx
│       │   ├── GALP 27082025__padrao_3__16974249000138__31122024__c75d513f.xlsx
│       │   ├── GALP ENERGIA 10_11_2022__75568a79.xlsx
│       │   ├── GALP ENERGIA 10_11_2022__padrao_2__42126753000198__31122021__75568a79.xlsx
│       │   ├── GAMA_06_09_2021__69638f8f.xlsx
│       │   ├── GAMA_06_09_2021__padrao_2__11251784000147__31122020__69638f8f.xlsx
│       │   ├── GENCO 23042024__1f02d39d.xlsx
│       │   ├── GENCO 23042024__padrao_6__30840548000100__31122023__1f02d39d.xlsx
│       │   ├── GENCO_04042023__0e683f92.xlsx
│       │   ├── Genco_22_05_2025__8e613430.xlsx
│       │   ├── Genco_22_05_2025__padrao_3__30840548000100__31122024__8e613430.xlsx
│       │   ├── GENIAL 12_04_2022__27639d35.xlsx
│       │   ├── GENIAL 12_04_2022__padrao_2__18483400000160__31122021__27639d35.xlsx
│       │   ├── Genial 20052025__f40c5b91.xlsx
│       │   ├── Genial 20052025__padrao_3__18483400000160__31122024__f40c5b91.xlsx
│       │   ├── GENIAL 27102023__e2b1ffbc.xlsx
│       │   ├── GENIAL 27102023__padrao_3__18483400000160__31122022__e2b1ffbc.xlsx
│       │   ├── GENIAL ENERGY 15072026__b01b333b.xlsx
│       │   ├── GENIAL ENERGY 15072026__padrao_6__18483400000160__31122025__b01b333b.xlsx
│       │   ├── GENIAL_06_09_2021__d7aecd1e.xlsx
│       │   ├── GENIAL_06_09_2021__padrao_2__18483400000160__31122020__d7aecd1e.xlsx
│       │   ├── GENIAL_17.05.2024__110d0711.xlsx
│       │   ├── GENIAL_17.05.2024__padrao_3__18483400000160__31122023__110d0711.xlsx
│       │   ├── GERAMAMORE 27082025__64365582.xlsx
│       │   ├── GERAMAMORE 27082025__padrao_3__09625739000163__31122024__64365582.xlsx
│       │   ├── GERAMAMORE_06.06.2024__4a38d113.xlsx
│       │   ├── GERAMAMORE_06.06.2024__padrao_3__09625739000163__31122023__4a38d113.xlsx
│       │   ├── GERAMAMORÉ 30112023__1132222a.xlsx
│       │   ├── GERAMAMORÉ 30112023__padrao_3__09625739000163__31122022__1132222a.xlsx
│       │   ├── GERAMAMORÉ RATING 00359795__8406352e.xlsx
│       │   ├── GERAMAMORÉ RATING 00359795__padrao_6__09625739000163__31122024__8406352e.xlsx
│       │   ├── GERAMAMORÉ_28_10_2021__4e5d9369.xlsx
│       │   ├── GERAMAMORÉ_28_10_2021__padrao_2__09625739000163__31122020__4e5d9369.xlsx
│       │   ├── Gerdau 01042026__4e9032f2.xlsx
│       │   ├── Gerdau 01042026__padrao_6__33611500000119__31122024__4e9032f2.xlsx
│       │   ├── GERDAU AÇOS LONGOS 23 04 2024__374624fd.xlsx
│       │   ├── GERDAU AÇOS LONGOS 23 04 2024__padrao_3__07358761000169__31122023__374624fd.xlsx
│       │   ├── Gerdau Aços Longos_20_09_2021__00abd54d.xlsx
│       │   ├── Gerdau Aços Longos_20_09_2021__padrao_2__07358761000169__31122020__00abd54d.xlsx
│       │   ├── GET_06_09_2021__6989cb95.xlsx
│       │   ├── GET_06_09_2021__padrao_2__31557781000143__31122020__6989cb95.xlsx
│       │   ├── GO ENERGY 25_05_2022__1a677df1.xlsx
│       │   ├── GO ENERGY 25_05_2022__padrao_2__28803705000166__31122021__1a677df1.xlsx
│       │   ├── GO ENERGY 29_11_2021__adecf520.xlsx
│       │   ├── GO ENERGY 29_11_2021__padrao_2__28803705000166__31122020__adecf520.xlsx
│       │   ├── GOLD 07_04_2022__cc2293ee.xlsx
│       │   ├── GOLD 07_04_2022__padrao_2__30483222000173__31122021__cc2293ee.xlsx
│       │   ├── GOLD 27032024 - Copia__505ee973.xlsx
│       │   ├── GOLD 27032024 - Copia__padrao_6__30483222000173__31122023__505ee973.xlsx
│       │   ├── GOLD _05_05_2021__4a4591e6.xlsx
│       │   ├── GOLD _05_05_2021__padrao_2__30483222000173__31122020__4a4591e6.xlsx
│       │   ├── GRID ENERGIA 04092025__669094fb.xlsx
│       │   ├── GRID ENERGIA 04092025__padrao_3__32618447000115__31122024__669094fb.xlsx
│       │   ├── GRID ENERGIA 23062026__6827712a.xlsx
│       │   ├── GRID ENERGIA 23062026__padrao_6__32618447000115__31122025__6827712a.xlsx
│       │   ├── Grupo BC_19052023__0d5ba623.xlsx
│       │   ├── HUMAITA 09062025__8478ec71.xlsx
│       │   ├── HUMAITA 09062025__padrao_3__25319200000132__31122024__8478ec71.xlsx
│       │   ├── HYDRO Energia 27022024__8125538b.xlsx
│       │   ├── HYDRO Energia 27022024__padrao_6__22109465000118__31122022__8125538b.xlsx
│       │   ├── HYDRO ENERGIA_2024__162611bb.xlsx
│       │   ├── HYDRO ENERGIA_2024__padrao_3__22109465000118__31122024__162611bb.xlsx
│       │   ├── HYDROENERGIA_19.06.2024__cfdbbc5f.xlsx
│       │   ├── HYDROENERGIA_19.06.2024__padrao_6__22109465000118__31122023__cfdbbc5f.xlsx
│       │   ├── IBITU 05122024 - Copia__e7963454.xlsx
│       │   ├── IBITU 05122024 - Copia__padrao_3__11820864000176__31122023__e7963454.xlsx
│       │   ├── IBITU 06_06_2022__fc0b5a79.xlsx
│       │   ├── IBITU 06_06_2022__padrao_2__11820864000176__31122021__fc0b5a79.xlsx
│       │   ├── IBITU 19062026__cbdc82ec.xlsx
│       │   ├── IBITU 19062026__padrao_6__11820864000176__31122025__cbdc82ec.xlsx
│       │   ├── IBITU RATING 11112025__b971cf7d.xlsx
│       │   ├── IBITU RATING 11112025__padrao_7__11820864000176__31122024__b971cf7d.xlsx
│       │   ├── IBS 13_06_2022__d792521d.xlsx
│       │   ├── IBS 13_06_2022__padrao_2__04462976000137__31122021__d792521d.xlsx
│       │   ├── IBS Energy_04082023__bd7fe3e2.xlsx
│       │   ├── IBS Energy_04082023__padrao_3__04462976000137__31122022__bd7fe3e2.xlsx
│       │   ├── IBS_09_09_2021__7024276d.xlsx
│       │   ├── IBS_09_09_2021__padrao_2__04462976000137__31122020__7024276d.xlsx
│       │   ├── IBS_24_06_2024__884ef836.xlsx
│       │   ├── IBS_24_06_2024__padrao_6__04462976000137__31122023__884ef836.xlsx
│       │   ├── ICAL ENERGIA 16042026__07a3fbee.xlsx
│       │   ├── IDEAL 25_05_2022 TESTE__2bc7c825.xlsx
│       │   ├── IDEAL 25_05_2022 TESTE__padrao_2__17070597000143__31122021__2bc7c825.xlsx
│       │   ├── IDEAL_09_09_2021__d80944d4.xlsx
│       │   ├── IDEAL_09_09_2021__padrao_2__17070597000143__31122020__d80944d4.xlsx
│       │   ├── IFT 04-05-2026__baa1490f.xlsx
│       │   ├── IFT 04-05-2026__padrao_6__15732189000184__31122024__baa1490f.xlsx
│       │   ├── IFT COM 27112023__a30fd095.xlsx
│       │   ├── IFT COM 27112023__padrao_3__15732189000184__31122022__a30fd095.xlsx
│       │   ├── IFT_09_09_2021__d30c00f3.xlsx
│       │   ├── IFT_09_09_2021__padrao_2__15732189000184__31122020__d30c00f3.xlsx
│       │   ├── IJUÍ 02072026__f86364cf.xlsx
│       │   ├── IJUÍ 02072026__padrao_6__07823304000106__31122025__f86364cf.xlsx
│       │   ├── IJUÍ 13072026__1dbd3b76.xlsx
│       │   ├── IJUÍ 13072026__padrao_6__07823304000106__31122025__1dbd3b76.xlsx
│       │   ├── INDRA 15_06_2022__14b06d68.xlsx
│       │   ├── INDRA 15_06_2022__padrao_2__32312466000119__31122021__14b06d68.xlsx
│       │   ├── INDRA 16072025__c61b94c1.xlsx
│       │   ├── INDRA 16072025__padrao_3__32312466000119__31122024__c61b94c1.xlsx
│       │   ├── INDRA_09_09_2021__b808eb6f.xlsx
│       │   ├── INDRA_09_09_2021__padrao_2__32312466000119__31122020__b808eb6f.xlsx
│       │   ├── INDRA_11042024__257706b1.xlsx
│       │   ├── INDRA_11042024__padrao_3__32312466000119__31122023__257706b1.xlsx
│       │   ├── INFINITY 04-05-2026__ac19ff57.xlsx
│       │   ├── INFINITY 04-05-2026__padrao_6__24479976000157__31122024__ac19ff57.xlsx
│       │   ├── INFINITY 08_08_2022__4fd5c0d8.xlsx
│       │   ├── INFINITY 08_08_2022__padrao_2__15732189000184__31122021__4fd5c0d8.xlsx
│       │   ├── INFINITY ENERGIAS 29_11_2021__2294e392.xlsx
│       │   ├── INFINITY ENERGIAS 29_11_2021__padrao_2__24479976000157__31122020__2294e392.xlsx
│       │   ├── Infinity_17.08.2023__8e52a1ea.xlsx
│       │   ├── Infinity_17.08.2023__padrao_3__24479976000157__31122022__8e52a1ea.xlsx
│       │   ├── INFINITY_20.05.2024 v2__09c71383.xlsx
│       │   ├── INFINITY_20.05.2024 v2__padrao_3__24479976000157__31122023__09c71383.xlsx
│       │   ├── INPASA 05082026__bf0bdbdd.xlsx
│       │   ├── INPASA 05082026__padrao_6__29316596000115__31122025__bf0bdbdd.xlsx
│       │   ├── IPIRA Energia S.A. - 00484431__2493b76a.xlsx
│       │   ├── IPIRA Energia S.A. - 00484431__padrao_6__26986376000100__31122025__2493b76a.xlsx
│       │   ├── ISFIDA RATING 05032026__7231d37a.xlsx
│       │   ├── ISFIDA RATING 05032026__padrao_6__21366458000139__31122024__7231d37a.xlsx
│       │   ├── ITAMBE ENERGETICA 29072026__be0aeebe.xlsx
│       │   ├── ITAMBE ENERGETICA 29072026__padrao_6__03926572000194__31122025__be0aeebe.xlsx
│       │   ├── ITAMBÉ ENERGÉTICA__78ea2864.xlsx
│       │   ├── ITAU 13062023__7985fd04.xlsx
│       │   ├── ITAU 13062023__padrao_3__31781135000165__31122022__7985fd04.xlsx
│       │   ├── ITAU 30102025__3ff996c5.xlsx
│       │   ├── ITAU 30102025__padrao_7__31781135000165__31122024__3ff996c5.xlsx
│       │   ├── ITAU COM 02_05_2022__eba60424.xlsx
│       │   ├── ITAU COM 28052026__1cc173b0.xlsx
│       │   ├── ITAU COM 28052026__padrao_6__31781135000165__31122025__1cc173b0.xlsx
│       │   ├── ITAU_05.07.2024__b55f7a2d.xlsx
│       │   ├── ITAU_05.07.2024__padrao_3__31781135000165__31122023__b55f7a2d.xlsx
│       │   ├── J&F 0108025__ae09502f.xlsx
│       │   ├── J&F 15092025__47eee93c.xlsx
│       │   ├── J&F 15092025__padrao_3__00350763000162__31122024__47eee93c.xlsx
│       │   ├── J&F 20082026__33c2a665.xlsx
│       │   ├── J&F 20082026__padrao_6__00350763002297__31122025__33c2a665.xlsx
│       │   ├── J&F DF 2024 holding__455fed23.xlsx
│       │   ├── J&F DF 2024 holding__padrao_6__00350763002297__31122024__455fed23.xlsx
│       │   ├── J&F RATING 06112025__6dd82a39.xlsx
│       │   ├── J&F RATING 06112025__padrao_7__31627849000113__31122024__6dd82a39.xlsx
│       │   ├── JANDAÍRA I ENERGIAS RENOVÁVEIS S.A._23.0__34e1d98c.xlsx
│       │   ├── JANDAÍRA I ENERGIAS RENOVÁVEIS S.A._23.0__padrao_3__35823538000180__31122023__34e1d98c.xlsx
│       │   ├── JANDAÍRA II ENERGIAS RENOVÁVEIS S.A._23.__4c716f55.xlsx
│       │   ├── JANDAÍRA II ENERGIAS RENOVÁVEIS S.A._23.__padrao_3__35824347000133__31122023__4c716f55.xlsx
│       │   ├── JANDAÍRA III ENERGIAS RENOVÁVEIS S.A._23__b297b155.xlsx
│       │   ├── JANDAÍRA III ENERGIAS RENOVÁVEIS S.A._23__padrao_3__35823536000191__31122023__b297b155.xlsx
│       │   ├── JANDAÍRA IV ENERGIAS RENOVÁVEIS S.A._23.__511294e3.xlsx
│       │   ├── JANDAÍRA IV ENERGIAS RENOVÁVEIS S.A._23.__padrao_3__35823577000188__31122023__511294e3.xlsx
│       │   ├── JARDIM BOTÂNICO GERAÇÃO 06052026__e2c3651c.xlsx
│       │   ├── JARDIM BOTÂNICO GERAÇÃO 06052026__padrao_6__24550050000100__31122025__e2c3651c.xlsx
│       │   ├── JBS_08.07.2024__d8ce4880.xlsx
│       │   ├── JBS_08.07.2024__padrao_3__02916265037837__31122023__d8ce4880.xlsx
│       │   ├── JSAFRA 15072026__df1455e9.xlsx
│       │   ├── JSAFRA 15072026__padrao_6__53012414000105__31122025__df1455e9.xlsx
│       │   ├── KROMA 17112023__833b4375.xlsx
│       │   ├── KROMA 17112023__padrao_6__10202852000115__31122022__833b4375.xlsx
│       │   ├── KROMA 31_05_2022__ea2489e8.xlsx
│       │   ├── KROMA 31_05_2022__padrao_2__10202852000115__31122021__ea2489e8.xlsx
│       │   ├── KROMA_24_05_2021__2efa29b2.xlsx
│       │   ├── KROMA_24_05_2021__padrao_2__10202852000115__31122020__2efa29b2.xlsx
│       │   ├── LAJARI ENERGETICA RATING 26012026__56c418e5.xlsx
│       │   ├── LAJARI ENERGETICA RATING 26012026__padrao_6__09020211000160__31122024__56c418e5.xlsx
│       │   ├── LDC 30062025__db49c172.xlsx
│       │   ├── LDC BRASIL 29102025__6044d919.xlsx
│       │   ├── LIBHERTA 01_06_2022__60731e81.xlsx
│       │   ├── LIBHERTA 01_06_2022__padrao_2__33127947000117__31122021__60731e81.xlsx
│       │   ├── LIBRA 05052026__68d283fa.xlsx
│       │   ├── LIBRA 05052026__padrao_6__20557422000170__31122025__68d283fa.xlsx
│       │   ├── LIBRA 29 04 2024__d85df5da.xlsx
│       │   ├── LIBRA 29 04 2024__padrao_6__20557422000170__31122023__d85df5da.xlsx
│       │   ├── LIBRA 30_05_2022__d4173325.xlsx
│       │   ├── LIBRA 30_05_2022__padrao_2__20557422000170__31122021__d4173325.xlsx
│       │   ├── LIBRA COMERCIALIZADORA 01102025__1cde6f8d.xlsx
│       │   ├── LIBRA COMERCIALIZADORA 01102025__padrao_3__20557422000170__31122024__1cde6f8d.xlsx
│       │   ├── LIBRA COMERCIALIZADORA 27032026__e650d426.xlsx
│       │   ├── LIBRA COMERCIALIZADORA 27032026__padrao_6__20557422000170__31122024__e650d426.xlsx
│       │   ├── LIBRA_09_09_2021__0be72f07.xlsx
│       │   ├── LIBRA_09_09_2021__padrao_2__20557422000170__31122020__0be72f07.xlsx
│       │   ├── LIBRA_2024__ce144345.xlsx
│       │   ├── LIBRA_2024__padrao_3__20557422000170__31122024__ce144345.xlsx
│       │   ├── LIGHT 18 04 2024__f64d0fc2.xlsx
│       │   ├── LIGHT 18 04 2024__padrao_3__11315117000180__31122023__f64d0fc2.xlsx
│       │   ├── LIGHT COM  RATING 22122025__a0b7ecaa.xlsx
│       │   ├── LIGHT COM  RATING 22122025__padrao_6__11315117000180__31122024__a0b7ecaa.xlsx
│       │   ├── LIGHT COM 07052026__3d8d442c.xlsx
│       │   ├── LIGHT COM 07052026__padrao_6__11315117000180__31122025__3d8d442c.xlsx
│       │   ├── LIGHT_(GRUPO)_18_10_2021__248c6e35.xlsx
│       │   ├── LIGHT_10_09_2021__7fdf3f55.xlsx
│       │   ├── LIGHT_10_09_2021__padrao_2__11315117000180__31122020__7fdf3f55.xlsx
│       │   ├── LIGHT_2024__7d930785.xlsx
│       │   ├── LIGHT_2024__padrao_3__11315117000180__31122024__7d930785.xlsx
│       │   ├── LIVEN 22042026__eb2cb353.xlsx
│       │   ├── LIVEN 22042026__padrao_6__43344428000164__31122025__eb2cb353.xlsx
│       │   ├── LIVEN COM 17092025__a8970887.xlsx
│       │   ├── LIVEN COM 17092025__padrao_3__43344428000164__31122024__a8970887.xlsx
│       │   ├── LOG 27112023__4ef3cc29.xlsx
│       │   ├── LOG 27112023__padrao_6__15042149000100__31122022__4ef3cc29.xlsx
│       │   ├── LOG ENERGIA 01_06_2022__c29458e8.xlsx
│       │   ├── LOG ENERGIA 01_06_2022__padrao_2__15042149000100__31122021__c29458e8.xlsx
│       │   ├── LOG ENERGIA 29092025__f1f2d555.xlsx
│       │   ├── LOG ENERGIA 29092025__padrao_3__15042149000100__31122024__f1f2d555.xlsx
│       │   ├── LOG_10_09_2021__a6427357.xlsx
│       │   ├── LOG_10_09_2021__padrao_2__15042149000100__31122020__a6427357.xlsx
│       │   ├── LOG_17.05.2024__eb3bf814.xlsx
│       │   ├── LOG_17.05.2024__padrao_3__15042149000100__31122023__eb3bf814.xlsx
│       │   ├── LOTUS_13.06.2024__3c0abe1e.xlsx
│       │   ├── LOTUS_13.06.2024__padrao_6__41806999000148__31122023__3c0abe1e.xlsx
│       │   ├── LUDFOR 08052025__4af5f07e.xlsx
│       │   ├── LUDFOR 08052025__padrao_3__29270235000185__31122024__4af5f07e.xlsx
│       │   ├── LUDFOR 11062026__60f48894.xlsx
│       │   ├── LUDFOR 11062026__padrao_6__35224835000100__31122025__60f48894.xlsx
│       │   ├── LUDFOR COM 08052025__27d3b134.xlsx
│       │   ├── LUDFOR COM 08052025__padrao_3__29270235000185__31122024__27d3b134.xlsx
│       │   ├── Ludfor geradora 16072026__dcaf5e26.xlsx
│       │   ├── Ludfor geradora 16072026__padrao_6__35224835000100__31122025__dcaf5e26.xlsx
│       │   ├── LUDFOR_09_09_2021__94477d4f.xlsx
│       │   ├── LUDFOR_09_09_2021__padrao_2__07725608000122__31122020__94477d4f.xlsx
│       │   ├── LUDFOR_19062023__a190fd00.xlsx
│       │   ├── LUDFOR_19062023__padrao_3__29270235000185__31122022__a190fd00.xlsx
│       │   ├── LUDFOR_20.05.2024__490a8af6.xlsx
│       │   ├── LUDFOR_20.05.2024__padrao_6__29270235000185__31122023__490a8af6.xlsx
│       │   ├── LUX 01_06_2022__8d1ee995.xlsx
│       │   ├── LUX 01_06_2022__padrao_2__28397998000129__31122021__8d1ee995.xlsx
│       │   ├── LUX 19082026__edec85fc.xlsx
│       │   ├── LUX 19082026__padrao_6__28397998000129__31122025__edec85fc.xlsx
│       │   ├── LUX 21052025__3bba6dae.xlsx
│       │   ├── LUX 21052025__padrao_3__28397998000129__31122024__3bba6dae.xlsx
│       │   ├── LUX RATING 02032026__09e3ba09.xlsx
│       │   ├── LUX RATING 02032026__padrao_6__28397998000129__31122024__09e3ba09.xlsx
│       │   ├── LÉROS_10_09_2021__b05417da.xlsx
│       │   ├── LÉROS_10_09_2021__padrao_2__11017349000152__31122020__b05417da.xlsx
│       │   ├── MARACANA 06082026__859dee94.xlsx
│       │   ├── MARACANA 06082026__padrao_6__08032643000129__31122025__859dee94.xlsx
│       │   ├── MARACANÃ ENERGÉTICA RATING 22012026__cedbcca7.xlsx
│       │   ├── MARACANÃ ENERGÉTICA RATING 22012026__padrao_6__08032643000129__31122024__cedbcca7.xlsx
│       │   ├── MASSARI_13.06.2024__289bcfd5.xlsx
│       │   ├── MASSARI_13.06.2024__padrao_6__38183972000131__31122023__289bcfd5.xlsx
│       │   ├── Matrix -grupo- 03042025(Recuperado Autom__fcbd7d96.xlsx
│       │   ├── Matrix -grupo- 03042025(Recuperado Autom__padrao_3__17858631000149__31122024__fcbd7d96.xlsx
│       │   ├── Matrix -grupo- 03042025__de6b095c.xlsx
│       │   ├── MATRIX 26_05_2022__6f9541c0.xlsx
│       │   ├── MATRIX 26_05_2022__padrao_2__17858631000149__31122021__6f9541c0.xlsx
│       │   ├── MATRIX COM 17072026__ae8a1177.xlsx
│       │   ├── MATRIX COM 17072026__padrao_6__17858631000149__31122025__ae8a1177.xlsx
│       │   ├── Matrix Grupo 1 11032024__abffc18f.xlsx
│       │   ├── Matrix Grupo 1 11032024__padrao_3__17858631000149__31122022__abffc18f.xlsx
│       │   ├── MATRIX_18_06_2021__3c2f6c35.xlsx
│       │   ├── MATRIX_18_06_2021__padrao_2__17858631000149__31122020__3c2f6c35.xlsx
│       │   ├── MATRIX_19.06.2024__ab4ec03c.xlsx
│       │   ├── MATRIX_19.06.2024__padrao_6__17858631000149__31122023__ab4ec03c.xlsx
│       │   ├── MATRIX_PURA_03042025__702ddb11.xlsx
│       │   ├── MATRIX_PURA_03042025__padrao_3__17858631000149__31122024__702ddb11.xlsx
│       │   ├── MAXIMA 01_02_2023__f8498528.xlsx
│       │   ├── MAXIMA 01_02_2023__padrao_2__12630054000110__31122021__f8498528.xlsx
│       │   ├── Maxima 21112023__cade6e01.xlsx
│       │   ├── Maxima 21112023__padrao_3__12630054000110__31122022__cade6e01.xlsx
│       │   ├── MAXIMA_18_06_2021__e92e46ab.xlsx
│       │   ├── MAXIMA_18_06_2021__padrao_2__12630054000110__31122020__e92e46ab.xlsx
│       │   ├── MAXIMA_21.05.2024__c106e40a.xlsx
│       │   ├── MAXIMA_21.05.2024__padrao_6__12630054000110__31122023__c106e40a.xlsx
│       │   ├── MEGA 04_07_2022__007a1672.xlsx
│       │   ├── MEGA 04_07_2022__padrao_2__15054480000140__31122021__007a1672.xlsx
│       │   ├── MEGA WATT_26_10_2021__63de4112.xlsx
│       │   ├── MEGA WATT_26_10_2021__padrao_2__15027346000150__31122020__63de4112.xlsx
│       │   ├── MEGA_12052023__5105964e.xlsx
│       │   ├── MEGA_12052023__padrao_4__15054480000140__31122022__5105964e.xlsx
│       │   ├── MEGA_16_09_2021__c5563bf8.xlsx
│       │   ├── MEGA_16_09_2021__padrao_2__15054480000140__31122020__c5563bf8.xlsx
│       │   ├── MEGA_20.06.2024__020c4e30.xlsx
│       │   ├── MEGA_20.06.2024__padrao_3__15054480000140__31122023__020c4e30.xlsx
│       │   ├── MENDUBIM GERAÇÃO 19112024__afef9426.xlsx
│       │   ├── MENDUBIM GERAÇÃO 19112024__padrao_3__37640312000170__31122023__afef9426.xlsx
│       │   ├── MERCATTO COM RATING 14012026__126451a6.xlsx
│       │   ├── MERCATTO COM RATING 14012026__padrao_6__21484454000155__31122024__126451a6.xlsx
│       │   ├── MERCATTOCOM_13.05.2024__95c30d88.xlsx
│       │   ├── MERCATTOCOM_13.05.2024__padrao_6__37028928000194__31122023__95c30d88.xlsx
│       │   ├── MERCATTOENERGIA_13.05.2024__59737d54.xlsx
│       │   ├── MERCATTOENERGIA_13.05.2024__padrao_3__21484454000155__31122023__59737d54.xlsx
│       │   ├── MERCURIO_13.05.2024__1778b966.xlsx
│       │   ├── MERCURIO_13.05.2024__padrao_6__29362082000104__31122023__1778b966.xlsx
│       │   ├── MERITO 14_11_2022__217e5f6d.xlsx
│       │   ├── MERITO 14_11_2022__padrao_2__26474919000100__31122021__217e5f6d.xlsx
│       │   ├── MERITO_18_06_2021__c51b9340.xlsx
│       │   ├── MERITO_18_06_2021__padrao_2__26474919000100__31122020__c51b9340.xlsx
│       │   ├── MEZ 12122023__f0dc8c61.xlsx
│       │   ├── MEZ 12122023__padrao_6__36537518000106__31122022__f0dc8c61.xlsx
│       │   ├── MIGRATIO 02072025__b8ed4f47.xlsx
│       │   ├── MIGRATIO 02072025__padrao_3__15458171000136__31122024__b8ed4f47.xlsx
│       │   ├── MIGRATIO 02_06_2022__00244288.xlsx
│       │   ├── MIGRATIO 02_06_2022__padrao_2__15458171000136__31122021__00244288.xlsx
│       │   ├── Migratio_07062023__225ebb2c.xlsx
│       │   ├── Migratio_07062023__padrao_3__15458171000136__31122022__225ebb2c.xlsx
│       │   ├── MIGRATIO_17_06_2021__7be0d074.xlsx
│       │   ├── MIGRATIO_17_06_2021__padrao_2__15458171000136__31122020__7be0d074.xlsx
│       │   ├── MINERVA 02_06_2022__ec4aeff3.xlsx
│       │   ├── MINERVA 02_06_2022__padrao_2__24510849000173__31122021__ec4aeff3.xlsx
│       │   ├── MINERVA 05_06_2025__b84e37de.xlsx
│       │   ├── MINERVA 05_06_2025__padrao_3__24510849000173__31122024__b84e37de.xlsx
│       │   ├── MINERVA 25 04 2024__af341e14.xlsx
│       │   ├── MINERVA 25 04 2024__padrao_6__24510849000173__31122023__af341e14.xlsx
│       │   ├── MINERVA COM 04082026__8a825089.xlsx
│       │   ├── MINERVA COM 04082026__padrao_6__24510849000173__31122025__8a825089.xlsx
│       │   ├── MINERVA RATING__3ae79617.xlsx
│       │   ├── MINERVA RATING__padrao_6__24510849000173__31122024__3ae79617.xlsx
│       │   ├── Minerva_12062023__86e230cf.xlsx
│       │   ├── Minerva_12062023__padrao_3__24510849000173__31122022__86e230cf.xlsx
│       │   ├── NC ENERGIA 21_06_2022__5235ca9e.xlsx
│       │   ├── NC_30.07.2024__546df139.xlsx
│       │   ├── NC_30.07.2024__padrao_3__04023261000188__31122023__546df139.xlsx
│       │   ├── NEC ENERGIA 06072026__9e0e163e.xlsx
│       │   ├── NEC ENERGIA 06072026__padrao_6__54252354000152__31122025__9e0e163e.xlsx
│       │   ├── NEC ENERGIA 18082026__a7b6a589.xlsx
│       │   ├── NEC ENERGIA 18082026__padrao_6__38126813000103__31122025__a7b6a589.xlsx
│       │   ├── NEC GERACAO 18082026__23ace549.xlsx
│       │   ├── NEC GERACAO 18082026__padrao_6__54252354000152__31122025__23ace549.xlsx
│       │   ├── NEO ENERGIA 01102025__b15c69f1.xlsx
│       │   ├── NEO ENERGIA 01102025__padrao_3__04023261000188__25032025__b15c69f1.xlsx
│       │   ├── Neoenergia 25082023__61fbc8a1.xlsx
│       │   ├── Neoenergia 25082023__padrao_3__04023261000188__31122022__61fbc8a1.xlsx
│       │   ├── NEOENERGIA RATING 24032026__0363dafb.xlsx
│       │   ├── NEOENERGIA RATING 24032026__padrao_6__04023261000188__31122024__0363dafb.xlsx
│       │   ├── NEW COM 02_08_2022__d52c740b.xlsx
│       │   ├── NEW COM 02_08_2022__padrao_2__28758086000135__31122021__d52c740b.xlsx
│       │   ├── NEWAVE 15042024__9d1b48e1.xlsx
│       │   ├── NEWAVE 15042024__padrao_6__42823087000147__31122023__9d1b48e1.xlsx
│       │   ├── NEWAVE 27032026__712a1d3c.xlsx
│       │   ├── NEWAVE 27032026__padrao_6__33524912000111__31122024__712a1d3c.xlsx
│       │   ├── NEWAVE_2024__75265778.xlsx
│       │   ├── NEWAVE_2024__padrao_3__42823087000147__31122024__75265778.xlsx
│       │   ├── NEWCOM RATING 27012026__66c7f27b.xlsx
│       │   ├── NEWCOM RATING 27012026__padrao_6__28758086000135__31122024__66c7f27b.xlsx
│       │   ├── NEWCOM_09102024__943529c1.xlsx
│       │   ├── NEWCOM_09102024__padrao_3__28758086000135__31122023__943529c1.xlsx
│       │   ├── NEWCOM_19072023__22fec522.xlsx
│       │   ├── NEWCOM_19072023__padrao_3__28758086000135__31122022__22fec522.xlsx
│       │   ├── NEWEN_09_09_2021__ea8986d7.xlsx
│       │   ├── NEWEN_09_09_2021__padrao_2__32235159000181__31072020__ea8986d7.xlsx
│       │   ├── NORSK HYDRO 16042026__7323a0ca.xlsx
│       │   ├── NORSK HYDRO 16042026__padrao_6__22109465000118__31122025__7323a0ca.xlsx
│       │   ├── NORSK HYDRO ENERGIA 09072026__a3b44950.xlsx
│       │   ├── NORSK HYDRO ENERGIA 09072026__padrao_6__22109465000118__31122025__a3b44950.xlsx
│       │   ├── NORTE ENERGIA 14052026__f85081b0.xlsx
│       │   ├── NORTE ENERGIA 14052026__padrao_6__12300288000107__31122025__f85081b0.xlsx
│       │   ├── NOVA 25 04 2024__e0eb18da.xlsx
│       │   ├── NOVA 25 04 2024__padrao_6__11182210000164__31122023__e0eb18da.xlsx
│       │   ├── NOVA ENERGIA 08_06_2022__b96ea78a.xlsx
│       │   ├── NOVA ENERGIA 08_06_2022__padrao_2__11182210000164__31122021__b96ea78a.xlsx
│       │   ├── Nova Energia_16_06_2021__22334954.xlsx
│       │   ├── Nova Energia_16_06_2021__padrao_2__11182210000164__31122020__22334954.xlsx
│       │   ├── NOVA GUAPORE 12082026__ee710d7b.xlsx
│       │   ├── NOVA GUAPORE 12082026__padrao_6__22976970000160__31122025__ee710d7b.xlsx
│       │   ├── NOVA_ENERGIA2024__21316198.xlsx
│       │   ├── NOVA_ENERGIA2024__padrao_6__11182210000164__31122024__21316198.xlsx
│       │   ├── OLYMPE 1311223__820d073e.xlsx
│       │   ├── OLYMPE 1311223__padrao_3__32168500000123__31122022__820d073e.xlsx
│       │   ├── OLYMPE 24042024__f7c4389b.xlsx
│       │   ├── OLYMPE 24042024__padrao_3__32168500000123__31122023__f7c4389b.xlsx
│       │   ├── OLYMPE 26_10_2022__3b319473.xlsx
│       │   ├── OLYMPE 26_10_2022__padrao_2__32168500000123__31122021__3b319473.xlsx
│       │   ├── OMEGA 13_07_2022__589c0c3a.xlsx
│       │   ├── OMG_07062023__5873e3ec.xlsx
│       │   ├── OMG_07062023__padrao_3__09149503000106__31122022__5873e3ec.xlsx
│       │   ├── PACIFICO 18032024__000231e2.xlsx
│       │   ├── PACIFICO 18032024__padrao_6__45829681000133__31122023__000231e2.xlsx
│       │   ├── PACIFICO_10062023__2a5871f6.xlsx
│       │   ├── PACIFICO_10062023__padrao_3__45829681000133__31122022__2a5871f6.xlsx
│       │   ├── PACTO 25 04 2024__7cbf7dd5.xlsx
│       │   ├── PACTO 25 04 2024__padrao_6__23412242000198__31122023__7cbf7dd5.xlsx
│       │   ├── PACTO_11.08.2023__f4df26df.xlsx
│       │   ├── PACTO_11.08.2023__padrao_3__23412242000198__31122022__f4df26df.xlsx
│       │   ├── PACTO_2024__5218a1c5.xlsx
│       │   ├── PACTO_2024__padrao_3__23412242000198__31122024__5218a1c5.xlsx
│       │   ├── PAECOM 29052026__c1325cbb.xlsx
│       │   ├── PAECOM 29052026__padrao_6__48251703000119__31122024__c1325cbb.xlsx
│       │   ├── PANENERGY 05042024__00ad2d39.xlsx
│       │   ├── PANENERGY 05042024__padrao_3__48251703000119__31122023__00ad2d39.xlsx
│       │   ├── PARACATU RATING 26022026__6c4f5db3.xlsx
│       │   ├── PARACATU RATING 26022026__padrao_6__08793343000162__31032025__6c4f5db3.xlsx
│       │   ├── PARATY 02_06_2022__f35fef5b.xlsx
│       │   ├── PARATY 02_06_2022__padrao_2__31102147000116__31122021__f35fef5b.xlsx
│       │   ├── Paraty 28062024__408a2c07.xlsx
│       │   ├── Paraty 28062024__padrao_6__31102147000116__31122023__408a2c07.xlsx
│       │   ├── PARATY ENERGIA 01102025__67ae7194.xlsx
│       │   ├── PARATY ENERGIA 01102025__padrao_3__31102147000116__31122024__67ae7194.xlsx
│       │   ├── Paraty Energia_30052023__70b3a0d5.xlsx
│       │   ├── Paraty Energia_30052023__padrao_3__31102147000116__31122022__70b3a0d5.xlsx
│       │   ├── PARATY_05.07.2024__93ab2aa0.xlsx
│       │   ├── PARATY_05.07.2024__padrao_3__34867956000107__31122023__93ab2aa0.xlsx
│       │   ├── Passo_5_Sao_Martinho_Rating_Final__a318b51b.xlsx
│       │   ├── PBEN_12.06.2024__f858139b.xlsx
│       │   ├── PBEN_12.06.2024__padrao_3__03538572000117__31122023__f858139b.xlsx
│       │   ├── PCH - NOVA GUARPORE RATING__944c1420.xlsx
│       │   ├── PCH - NOVA GUARPORE RATING__padrao_6__22976970000160__31122024__944c1420.xlsx
│       │   ├── PCH MOINHO  RATING 26012026__8df084e0.xlsx
│       │   ├── PCH MOINHO  RATING 26012026__padrao_6__21467516000110__31122024__8df084e0.xlsx
│       │   ├── PCH VERDE 2 ENERGETICA RATING 23012026__f23e1ada.xlsx
│       │   ├── PETRA 09_03_ 2022__f297efd3.xlsx
│       │   ├── PETRA 09_03_ 2022__padrao_2__28120534000170__31122021__f297efd3.xlsx
│       │   ├── PETRA_06_05_2021( modelo novo)__185fe1b2.xlsx
│       │   ├── PETRA_06_05_2021( modelo novo)__padrao_2__28120534000170__31122020__185fe1b2.xlsx
│       │   ├── PETROBRAS PIE 03062025__c5a25860.xlsx
│       │   ├── PETROBRAS PIE 03062025__padrao_3__33000167000101__31122024__c5a25860.xlsx
│       │   ├── PIE RP 17_11_2022__f472e843.xlsx
│       │   ├── PIE RP 17_11_2022__padrao_2__04810290000190__31122021__f472e843.xlsx
│       │   ├── PLURAL ENERGIA 20_07_2022__714c5565.xlsx
│       │   ├── PLURAL ENERGIA 20_07_2022__padrao_2__29270235000185__31122021__714c5565.xlsx
│       │   ├── POLLARIX 03062026__10fd5d33.xlsx
│       │   ├── POLLARIX 03062026__padrao_6__04755710000182__31122025__10fd5d33.xlsx
│       │   ├── PONTOON 10072025__7046e5c8.xlsx
│       │   ├── PONTOON 10072025__padrao_3__39237248000106__31122024__7046e5c8.xlsx
│       │   ├── PONTOON_29_08_2024__1bbe5304.xlsx
│       │   ├── PONTOON_29_08_2024__padrao_3__39237248000106__31122023__1bbe5304.xlsx
│       │   ├── POWER COM 02_05_2022__f61cf2f4.xlsx
│       │   ├── POWER COM 02_05_2022__padrao_2__22153641000119__31122021__f61cf2f4.xlsx
│       │   ├── POWER COM 14_06_2022__3273497e.xlsx
│       │   ├── POWER COM 14_06_2022__padrao_2__29883520000171__31122021__3273497e.xlsx
│       │   ├── PRIME ENERGY 02_06_2022__f08a2704.xlsx
│       │   ├── PRIME ENERGY 02_06_2022__padrao_2__17040615000144__31122021__f08a2704.xlsx
│       │   ├── PRIME ENERGY 02_08_2022__772478b8.xlsx
│       │   ├── PRIME ENERGY 02_08_2022__padrao_2__12809025000110__31122021__772478b8.xlsx
│       │   ├── PRIME ENERGY _21_06_2021__74a55640.xlsx
│       │   ├── PRIME ENERGY _21_06_2021__padrao_2__12809025000110__31122020__74a55640.xlsx
│       │   ├── PRIME_12.07.2024__113162fb.xlsx
│       │   ├── PRIME_12.07.2024__padrao_6__12809025000110__31122023__113162fb.xlsx
│       │   ├── PRIME_16.06.2023__ff583239.xlsx
│       │   ├── PRIME_16.06.2023__padrao_3__12809025000110__31122022__ff583239.xlsx
│       │   ├── PWR ENERGIA_15_06_2021__b32a6c89.xlsx
│       │   ├── PWR ENERGIA_15_06_2021__padrao_2__29883520000171__31122020__b32a6c89.xlsx
│       │   ├── QAIR 01042026__f04e04fb.xlsx
│       │   ├── QAIR 01042026__padrao_6__08666285000106__31122024__f04e04fb.xlsx
│       │   ├── QAIR BRASIL (iniciante)_10_10_22__987c84a7.xlsx
│       │   ├── QAIR BRASIL (iniciante)_10_10_22__padrao_2__39608949000104__31122021__987c84a7.xlsx
│       │   ├── QAIR_13.06.2024__2c3c16ba.xlsx
│       │   ├── QAIR_13.06.2024__padrao_6__39608949000104__31122023__2c3c16ba.xlsx
│       │   ├── RAHCROL_10_09_2021__aede84c6.xlsx
│       │   ├── RAHCROL_10_09_2021__padrao_2__09222477000196__31122019__aede84c6.xlsx
│       │   ├── RBE 01072025__d984855c.xlsx
│       │   ├── RBE 01072025__padrao_3__13338734000127__31122024__d984855c.xlsx
│       │   ├── RBE 15_06_2022__e6f689af.xlsx
│       │   ├── RBE 15_06_2022__padrao_2__13338734000127__31122021__e6f689af.xlsx
│       │   ├── RBE 31102023__e1121fdf.xlsx
│       │   ├── RBE 31102023__padrao_6__13338734000127__31122022__e1121fdf.xlsx
│       │   ├── RBE_05.06.2024__b9c0c665.xlsx
│       │   ├── RBE_05.06.2024__padrao_3__13338734000127__31122023__b9c0c665.xlsx
│       │   ├── RENOVA 12062026__3e542cef.xlsx
│       │   ├── RENOVA 12062026__padrao_6__17204923000168__31122025__3e542cef.xlsx
│       │   ├── RENOVA 26082025__86b07de8.xlsx
│       │   ├── RENOVA 26082025__padrao_3__17204923000168__31122024__86b07de8.xlsx
│       │   ├── RENOVA BR RI__0e08d072.xlsx
│       │   ├── RENOVA BR RI__padrao_6__17204923000168__31122024__0e08d072.xlsx
│       │   ├── RENOVA COM 27082025__281cb87f.xlsx
│       │   ├── RENOVA COM 27082025__padrao_3__17204923000168__31122024__281cb87f.xlsx
│       │   ├── RIALMA V 06072026__b72fcdc8.xlsx
│       │   ├── RIALMA V 06072026__padrao_6__11040403000180__31122025__b72fcdc8.xlsx
│       │   ├── Rio Canoas (CTG) 17042026__f2bfaa57.xlsx
│       │   ├── Rio Canoas (CTG) 17042026__padrao_6__11316814000156__31122024__f2bfaa57.xlsx
│       │   ├── RIO ENERGY (GRUPO) 23_08_2022__f0034f11.xlsx
│       │   ├── RIO ENERGY 17_11_2021__9c912766.xlsx
│       │   ├── RIO ENERGY 17_11_2021__padrao_2__16775973000132__05022021__9c912766.xlsx
│       │   ├── Rio Energy_28032023__eb110012.xlsx
│       │   ├── Rio Energy_28032023__padrao_3__16775973000132__31122022__eb110012.xlsx
│       │   ├── Rio Parana 14042026__2df8c55e.xlsx
│       │   ├── Rio Parana 14042026__padrao_6__23096269000119__31122024__2df8c55e.xlsx
│       │   ├── RIO PARANAPANEMA 13042026__91d0d374.xlsx
│       │   ├── RIO PARANAPANEMA 13042026__padrao_6__02998301000181__31122024__91d0d374.xlsx
│       │   ├── RZK 10112023__4b24aa1a.xlsx
│       │   ├── RZK 10112023__padrao_6__26562346000177__31122022__4b24aa1a.xlsx
│       │   ├── RZK_16.05.2024__bee67ee6.xlsx
│       │   ├── RZK_16.05.2024__padrao_3__26562346000177__31122023__bee67ee6.xlsx
│       │   ├── RZK_26_10_2021__5257321f.xlsx
│       │   ├── RZK_26_10_2021__padrao_2__26562346000177__31122020__5257321f.xlsx
│       │   ├── SAFIRA 08_06_2022__e849f835.xlsx
│       │   ├── SAFIRA 08_06_2022__padrao_2__11482752000152__31122021__e849f835.xlsx
│       │   ├── SAFIRA 11042024__3ff90bd0.xlsx
│       │   ├── SAFIRA 11042024__padrao_6__09495582000107__31122023__3ff90bd0.xlsx
│       │   ├── SAFIRA 27032026 DF 2024__ed3c1dfe.xlsx
│       │   ├── SAFIRA 27032026 DF 2024__padrao_6__09495582000107__31122024__ed3c1dfe.xlsx
│       │   ├── SAFIRA ADM__1492d833.xlsx
│       │   ├── SAFIRA ADM__padrao_3__09495582000107__31122024__1492d833.xlsx
│       │   ├── SAFIRA COM_05_03_2021__49134c2e.xlsx
│       │   ├── SAFIRA COM_05_03_2021__padrao_2__09495582000107__31122020__49134c2e.xlsx
│       │   ├── SAFIRA Holding 2023__aa03b24d.xlsx
│       │   ├── SAFIRA Holding__82276c7e.xlsx
│       │   ├── SAFIRA VAREJISTA_2023__1b47b800.xlsx
│       │   ├── SAFIRA VAREJISTA_2023__padrao_3__11482752000152__31122023__1b47b800.xlsx
│       │   ├── SAFIRA VAREJISTA_2024__6dcc8a81.xlsx
│       │   ├── SAFIRA VAREJISTA_2024__padrao_3__11482752000152__31122024__6dcc8a81.xlsx
│       │   ├── SAFIRA_12_05_2022__08338d1f.xlsx
│       │   ├── SAFIRA_12_05_2022__padrao_2__09495582000107__31122021__08338d1f.xlsx
│       │   ├── SAFIRA_27042023__99f0776a.xlsx
│       │   ├── SAFIRA_27042023__padrao_3__09495582000107__31122022__99f0776a.xlsx
│       │   ├── SAFRA 10072025__d0da1e45.xlsx
│       │   ├── SAFRA 10072025__padrao_3__53012414000105__31122024__d0da1e45.xlsx
│       │   ├── SANTA HELENA ENERGIA 15062026__c2ca5fd3.xlsx
│       │   ├── SANTA HELENA ENERGIA 15062026__padrao_6__12150746000160__31122025__c2ca5fd3.xlsx
│       │   ├── SANTA MARIA 11082026__55eb85fe.xlsx
│       │   ├── SANTA MARIA 11082026__padrao_6__32023463000165__31122025__55eb85fe.xlsx
│       │   ├── SANTA MARIA_09_09_2021__63627231.xlsx
│       │   ├── SANTA MARIA_09_09_2021__padrao_2__32023463000165__31122020__63627231.xlsx
│       │   ├── SANTA MARIA_16.05.2024__60afd5c4.xlsx
│       │   ├── SANTA MARIA_16.05.2024__padrao_6__32023463000165__31122023__60afd5c4.xlsx
│       │   ├── SANTA MARIA_2024__a60344ae.xlsx
│       │   ├── SANTA MARIA_2024__padrao_3__32023463000165__31122024__a60344ae.xlsx
│       │   ├── SANTADER_26.06.2024__dfd9038a.xlsx
│       │   ├── SANTADER_26.06.2024__padrao_3__04270778000171__31122023__dfd9038a.xlsx
│       │   ├── Santander 13062023__7af15b0c.xlsx
│       │   ├── Santander 13062023__padrao_3__04270778000171__31122022__7af15b0c.xlsx
│       │   ├── SANTANDER RATING 24102025__f7c82a17.xlsx
│       │   ├── SANTANDER RATING 24102025__padrao_7__04270778000171__31122024__f7c82a17.xlsx
│       │   ├── SEB 16102024__1__639eb619.xlsx
│       │   ├── SEB 16102024__1__padrao_3__27796415000170__31122023__639eb619.xlsx
│       │   ├── SEB 16102024__51772d3f.xlsx
│       │   ├── SEB 16102024__padrao_3__27796415000250__31122023__51772d3f.xlsx
│       │   ├── SEB RATING 17112025__a3afa918.xlsx
│       │   ├── SEB RATING 17112025__padrao_6__27796415000170__31122024__a3afa918.xlsx
│       │   ├── SEB RATING 2023__45a59683.xlsx
│       │   ├── SEB RATING 2023__padrao_6__27796415000170__31122024__45a59683.xlsx
│       │   ├── SEMPER 02062026__07da5258.xlsx
│       │   ├── SEMPER 02062026__padrao_6__48591179000125__31122025__07da5258.xlsx
│       │   ├── Semper_2024__4b0b08a6.xlsx
│       │   ├── Semper_2024__padrao_3__48591179000125__31122024__4b0b08a6.xlsx
│       │   ├── SERENA 15072025__d17afe85.xlsx
│       │   ├── SERENA 15072025__padrao_3__09149503000106__31122024__d17afe85.xlsx
│       │   ├── SERENA 18 04 2024__96b60b14.xlsx
│       │   ├── SERENA 18 04 2024__padrao_3__09149503000106__31122023__96b60b14.xlsx
│       │   ├── SERRA DAS VACAS HOLDING II__f7d815cc.xlsx
│       │   ├── SERRA DAS VACAS HOLDING II__padrao_6__24011952000179__31122025__f7d815cc.xlsx
│       │   ├── SGS BRASIL 10_03_2022__ed2b87d7.xlsx
│       │   ├── SGS BRASIL 10_03_2022__padrao_2__23422037000103__31122021__ed2b87d7.xlsx
│       │   ├── SGS Brasil 19-01-2023__b572d7cc.xlsx
│       │   ├── SGS Brasil 19-01-2023__padrao_3__09625739000163__31122021__b572d7cc.xlsx
│       │   ├── SHELL 07052026__0fbd1222.xlsx
│       │   ├── SHELL 07052026__padrao_6__27796415000170__31122025__0fbd1222.xlsx
│       │   ├── SHELL ENERGY 08_08_2022__cafc6c51.xlsx
│       │   ├── SHELL ENERGY 08_08_2022__padrao_2__27796415000170__31122021__cafc6c51.xlsx
│       │   ├── SIMPLE 02072026__f476c794.xlsx
│       │   ├── SIMPLE 02072026__padrao_6__15667402000111__31122025__f476c794.xlsx
│       │   ├── SIMPLE 06_06_2022__b655fe19.xlsx
│       │   ├── SIMPLE 06_06_2022__padrao_2__17112981000161__31122021__b655fe19.xlsx
│       │   ├── SIMPLE 27032024__b5de56ff.xlsx
│       │   ├── SIMPLE 27032024__padrao_6__17112981000161__31122023__b5de56ff.xlsx
│       │   ├── SIMPLE _14_06_2021__8850d969.xlsx
│       │   ├── SIMPLE _14_06_2021__padrao_2__17112981000161__31122020__8850d969.xlsx
│       │   ├── SIMPLE_2024__a77a62ff.xlsx
│       │   ├── SIMPLE_2024__padrao_3__17112981000161__31122024__a77a62ff.xlsx
│       │   ├── SIMPLE_22032023__da6e4eea.xlsx
│       │   ├── SKOPOS 02062026__65cf9a0a.xlsx
│       │   ├── SKOPOS 02062026__padrao_6__29340729000199__31122025__65cf9a0a.xlsx
│       │   ├── SKOPOS 08_08_2022__7a4dc0e5.xlsx
│       │   ├── SKOPOS 08_08_2022__padrao_2__29340729000199__31122021__7a4dc0e5.xlsx
│       │   ├── SKOPOS 24 04 2024__478b7aef.xlsx
│       │   ├── SKOPOS 24 04 2024__padrao_6__29340729000199__31122023__478b7aef.xlsx
│       │   ├── SKOPOS 26082025__f87033b0.xlsx
│       │   ├── SKOPOS 26082025__padrao_3__29340729000199__31122024__f87033b0.xlsx
│       │   ├── SKOPOS 27032026 df 2024__15d135d5.xlsx
│       │   ├── SKOPOS 27032026 df 2024__padrao_6__29340729000199__31122024__15d135d5.xlsx
│       │   ├── SKOPOS_09_09_2021__53fc0659.xlsx
│       │   ├── SKOPOS_09_09_2021__padrao_2__29340729000199__31122020__53fc0659.xlsx
│       │   ├── SKOPOS_14072023__fc8d1d04.xlsx
│       │   ├── SKOPOS_14072023__padrao_3__29340729000199__31122022__fc8d1d04.xlsx
│       │   ├── SOL SERRA DO MEL III SPE S.A_20.05.2024__544afe6b.xlsx
│       │   ├── SOL SERRA DO MEL III SPE S.A_20.05.2024__padrao_3__39702802000189__31122023__544afe6b.xlsx
│       │   ├── SOL SERRA DO MEL IV SPE S.A_20.05.2024__d75906ee.xlsx
│       │   ├── SOL SERRA DO MEL IV SPE S.A_20.05.2024__padrao_3__34818458000174__31122023__d75906ee.xlsx
│       │   ├── SOL SERRA DO MEL V SPE S.A_20.05.2024__661184df.xlsx
│       │   ├── SOL SERRA DO MEL V SPE S.A_20.05.2024__padrao_3__34818597000106__31122023__661184df.xlsx
│       │   ├── SOL SERRA DO MEL VI SPE S.A_20.05.2024__1732660c.xlsx
│       │   ├── SOL SERRA DO MEL VI SPE S.A_20.05.2024__padrao_3__29350168000109__31122023__1732660c.xlsx
│       │   ├── SOLAR ENERGIA RATING COM 13012026__fd47bb24.xlsx
│       │   ├── SOLAR ENERGIA RATING COM 13012026__padrao_6__41501877000143__31122024__fd47bb24.xlsx
│       │   ├── SOLENERGIAS 06_06_2022__90b51a69.xlsx
│       │   ├── SOLENERGIAS 06_06_2022__padrao_2__13459301000120__31122021__90b51a69.xlsx
│       │   ├── SOLENERGIAS_05.06.2024__97bdfedf.xlsx
│       │   ├── SOLENERGIAS_05.06.2024__padrao_3__13459301000120__31122023__97bdfedf.xlsx
│       │   ├── SPIC 13072026__f3959099.xlsx
│       │   ├── SPIC 13072026__padrao_6__42902392000124__31122025__f3959099.xlsx
│       │   ├── SPIC BRASIL 01_12_2022__bb47b707.xlsx
│       │   ├── SPIC BRASIL 07052026__c9b7ed23.xlsx
│       │   ├── SPIC BRASIL C 13112024__6a1e7d96.xlsx
│       │   ├── SPIC BRASIL C 13112024__padrao_3__42902392000124__31122023__6a1e7d96.xlsx
│       │   ├── SPIC COM 27062025__81227e61.xlsx
│       │   ├── SPIC COM 27062025__padrao_3__42902392000124__31122024__81227e61.xlsx
│       │   ├── SPOT_12.06.2024__f17c9baf.xlsx
│       │   ├── SPOT_12.06.2024__padrao_6__10466806000123__31122023__f17c9baf.xlsx
│       │   ├── SQUADRA 16_11_2022__5a811e79.xlsx
│       │   ├── SQUADRA 16_11_2022__padrao_2__30966130000144__31082022__5a811e79.xlsx
│       │   ├── SQUADRA_18 04 2024__7b58e28d.xlsx
│       │   ├── SQUADRA_18 04 2024__padrao_6__30966130000144__31122023__7b58e28d.xlsx
│       │   ├── Squadra_2024__9233086b.xlsx
│       │   ├── Squadra_2024__padrao_3__30966130000144__31122024__9233086b.xlsx
│       │   ├── SQUADRA_29032023__edf1b141.xlsx
│       │   ├── SQUADRA_29032023__padrao_3__30966130000144__31122022__edf1b141.xlsx
│       │   ├── STAKRAFT_05.07.2024__d39b0e2c.xlsx
│       │   ├── STAKRAFT_05.07.2024__padrao_3__08573833000153__31122023__d39b0e2c.xlsx
│       │   ├── STATKRAFT 13082026__494619dd.xlsx
│       │   ├── STATKRAFT 13082026__padrao_6__41808680000151__31122025__494619dd.xlsx
│       │   ├── STATKRAFT 24_06_2022__c5640328.xlsx
│       │   ├── STATKRAFT 27082025__61a05183.xlsx
│       │   ├── STATKRAFT 27082025__padrao_3__08573833000153__31122024__61a05183.xlsx
│       │   ├── STATKRAFT INVESTIMENTOS 29092025__1a3ba0cd.xlsx
│       │   ├── STATKRAFT INVESTIMENTOS 29092025__padrao_3__41808680000151__31122024__1a3ba0cd.xlsx
│       │   ├── STATKRAFT_29052023__0afd2afc.xlsx
│       │   ├── STIMA 06_06_2022__9b2e48bb.xlsx
│       │   ├── STIMA 06_06_2022__padrao_2__25099255000184__31122021__9b2e48bb.xlsx
│       │   ├── STIMA 11042024__645a1ce6.xlsx
│       │   ├── STIMA 11042024__padrao_6__25099255000184__31122023__645a1ce6.xlsx
│       │   ├── STIMA_10_09_2021__1cd9a896.xlsx
│       │   ├── STIMA_10_09_2021__padrao_2__25099255000184__31122020__1cd9a896.xlsx
│       │   ├── Stima_2024__3e98ba82.xlsx
│       │   ├── Stima_2024__padrao_3__25099255000184__31122024__3e98ba82.xlsx
│       │   ├── STIMA_30052023__6526e919.xlsx
│       │   ├── STIMA_30052023__padrao_4__25099255000184__31122022__6526e919.xlsx
│       │   ├── SUDOESTE ENERGIA 14_06_2022__3dd503c6.xlsx
│       │   ├── SUDOESTE ENERGIA 14_06_2022__padrao_2__03358698000100__31122021__3dd503c6.xlsx
│       │   ├── SUZANO 13122023__7b19111e.xlsx
│       │   ├── SUZANO 13122023__padrao_6__16404287000155__31122022__7b19111e.xlsx
│       │   ├── SUZANO_04.07.2024__8e8e10b6.xlsx
│       │   ├── SUZANO_04.07.2024__padrao_6__16404287067730__31122023__8e8e10b6.xlsx
│       │   ├── SUZANO_COPILOT__b889f691.xlsx
│       │   ├── TAKODA_13.06.2024__74ac0319.xlsx
│       │   ├── TAKODA_13.06.2024__padrao_3__35458657000181__31122023__74ac0319.xlsx
│       │   ├── TCCOM_18032024__519e4286.xlsx
│       │   ├── TCCOM_18032024__padrao_6__49983274000137__31122023__519e4286.xlsx
│       │   ├── TEMPO 08_08_2022__64d11f0d.xlsx
│       │   ├── TEMPO 08_08_2022__padrao_2__29000095000125__31122021__64d11f0d.xlsx
│       │   ├── TEMPO 20112023__d18b5780.xlsx
│       │   ├── TEMPO 20112023__padrao_6__29000095000125__31122022__d18b5780.xlsx
│       │   ├── Tempo Energia_10_06_2021__4e243f83.xlsx
│       │   ├── Tempo Energia_10_06_2021__padrao_2__29000095000125__31122020__4e243f83.xlsx
│       │   ├── TEMPO_21.05.2024__283b16fa.xlsx
│       │   ├── TEMPO_21.05.2024__padrao_6__29000095000125__31122023__283b16fa.xlsx
│       │   ├── TEREOS 15072026__ab514fad.xlsx
│       │   ├── TESLA 06_06_2022__1a5b1de1.xlsx
│       │   ├── TESLA 06_06_2022__padrao_2__20726794000182__31122021__1a5b1de1.xlsx
│       │   ├── THERA 08_08_2022__99f5d45d.xlsx
│       │   ├── THERA 08_08_2022__padrao_2__27690671000188__31122021__99f5d45d.xlsx
│       │   ├── THERA 30102025__98c33add.xlsx
│       │   ├── THERA 30102025__padrao_6__27690671000188__31122024__98c33add.xlsx
│       │   ├── THERA_04.06.2024__f4ba3508.xlsx
│       │   ├── THERA_04.06.2024__padrao_6__27690671000188__31122023__f4ba3508.xlsx
│       │   ├── THERA_08_06_2021__7d8f1ec0.xlsx
│       │   ├── THERA_08_06_2021__padrao_2__27690671000188__31122020__7d8f1ec0.xlsx
│       │   ├── THERA_10102023__59136fd4.xlsx
│       │   ├── THERA_10102023__padrao_3__27690671000188__31122022__59136fd4.xlsx
│       │   ├── THOPEN 09072025__1f16466d.xlsx
│       │   ├── THOPEN 09072025__padrao_3__26562346000177__31122024__1f16466d.xlsx
│       │   ├── THOPEN ENERGIA 20072026__23cda899.xlsx
│       │   ├── THOPEN ENERGIA 20072026__padrao_6__28133664000148__31122024__23cda899.xlsx
│       │   ├── THOPEN ENERGY RATING 28112025__19295889.xlsx
│       │   ├── THOPEN ENERGY RATING 28112025__padrao_6__26562346000177__31122024__19295889.xlsx
│       │   ├── TIMBRO TRADING 15072026__fb0ee68d.xlsx
│       │   ├── TRADENER 17052024__cfbceee6.xlsx
│       │   ├── TRADENER 17052024__padrao_6__02691745000170__31122023__cfbceee6.xlsx
│       │   ├── TRADENER 29_08_2022__6b4614b1.xlsx
│       │   ├── TRADENER 29_08_2022__padrao_2__02691745000170__31122021__6b4614b1.xlsx
│       │   ├── TRADENER_02_09_2021__3c15126f.xlsx
│       │   ├── TRADENER_02_09_2021__padrao_2__02691745000170__31122020__3c15126f.xlsx
│       │   ├── TRADENER_10042025__b5c7c6ef.xlsx
│       │   ├── TRADENER_10042025__padrao_3__02691745000170__31122024__b5c7c6ef.xlsx
│       │   ├── Tradener_15092023 - Copia__a45b0d14.xlsx
│       │   ├── Tradener_15092023 - Copia__padrao_3__02691745000170__31122022__a45b0d14.xlsx
│       │   ├── TRIA 04082026__d9003dbf.xlsx
│       │   ├── TRIA 04082026__padrao_6__46494301000110__31122025__d9003dbf.xlsx
│       │   ├── TRIA 22052025__8af98af7.xlsx
│       │   ├── TRIA 22052025__padrao_3__46494301000110__31122024__8af98af7.xlsx
│       │   ├── TRIA 27032026 df 2024__3f680707.xlsx
│       │   ├── TRIA 27032026 df 2024__padrao_6__46494301000110__31122024__3f680707.xlsx
│       │   ├── TRIA RATING 28102025__6172d0c3.xlsx
│       │   ├── TRIA RATING 28102025__padrao_6__46494301000110__31122024__6172d0c3.xlsx
│       │   ├── TRIA_03.06.2024__88020709.xlsx
│       │   ├── TRIA_03.06.2024__padrao_6__46494301000110__31122023__88020709.xlsx
│       │   ├── TRIEX 26032026__f7bad3da.xlsx
│       │   ├── TRIEX 26032026__padrao_6__50729198000117__31122025__f7bad3da.xlsx
│       │   ├── TRINITY 06_06_2022__ba876f81.xlsx
│       │   ├── TRINITY 06_06_2022__padrao_2__17077752000153__31122021__ba876f81.xlsx
│       │   ├── TRINITY ENERGIA_09_06_2021__ef69f26d.xlsx
│       │   ├── TRINITY ENERGIA_09_06_2021__padrao_2__17077752000153__31122020__ef69f26d.xlsx
│       │   ├── TRINITY_09062023__93012735.xlsx
│       │   ├── TRINITY_16.05.2024 v2__94ce3039.xlsx
│       │   ├── TRINITY_16.05.2024 v2__padrao_6__17077752000153__31122023__94ce3039.xlsx
│       │   ├── TRUE 14042026__6f808d56.xlsx
│       │   ├── TRUE 14042026__padrao_6__18185035000108__31122025__6f808d56.xlsx
│       │   ├── TRUE 22-05-2025__52cd156f.xlsx
│       │   ├── TRUE 22-05-2025__padrao_3__18185035000108__31122024__52cd156f.xlsx
│       │   ├── TRUE 22_03_2022__dce12cfc.xlsx
│       │   ├── TRUE 22_03_2022__padrao_2__18185035000108__31122021__dce12cfc.xlsx
│       │   ├── TRUE 29 04 2024__ab87271f.xlsx
│       │   ├── TRUE 29 04 2024__padrao_6__18185035000108__31122023__ab87271f.xlsx
│       │   ├── TRUE _06_05_2021__25dbfd0d.xlsx
│       │   ├── TRUE _06_05_2021__padrao_2__18185035000108__31122020__25dbfd0d.xlsx
│       │   ├── TRUE_31032023__098206bd.xlsx
│       │   ├── TYR 16072025__c52a0fab.xlsx
│       │   ├── TYR 16072025__padrao_3__29362082000104__31122024__c52a0fab.xlsx
│       │   ├── UHE SAO SIMAO 14052026__40e2d1e9.xlsx
│       │   ├── UHE SAO SIMAO 14052026__padrao_6__27352303000120__31122025__40e2d1e9.xlsx
│       │   ├── UHE SAO SIMAO 29082025__16d7c634.xlsx
│       │   ├── ULTRAGAZ 12122025__b49341d0.xlsx
│       │   ├── ULTRAGAZ 12122025__padrao_6__26914969000161__31122024__b49341d0.xlsx
│       │   ├── ULTRAGAZ 14052026__eb5d020c.xlsx
│       │   ├── ULTRAGAZ 14052026__padrao_6__26914969000161__31122025__eb5d020c.xlsx
│       │   ├── URCA 08_08_2022__9ee38172.xlsx
│       │   ├── URCA 08_08_2022__padrao_2__32185360000100__31122021__9ee38172.xlsx
│       │   ├── URCA 11 04 2024__129dbd66.xlsx
│       │   ├── URCA 11 04 2024__padrao_6__32185360000100__31122023__129dbd66.xlsx
│       │   ├── URCA_09_09_2021__59c3fa43.xlsx
│       │   ├── URCA_09_09_2021__padrao_2__32185360000100__31122020__59c3fa43.xlsx
│       │   ├── URUCUIA 23062026__6e006204.xlsx
│       │   ├── URUCUIA 23062026__padrao_6__55935046000194__31122025__6e006204.xlsx
│       │   ├── USINA MONTE ALEGRE 15072026__2d3f4b22.xlsx
│       │   ├── USINA MONTE ALEGRE 15072026__padrao_6__22587687000146__31122025__2d3f4b22.xlsx
│       │   ├── UTE VALE DO PARANA__598255a0.xlsx
│       │   ├── UTE VALE DO PARANA__padrao_6__05938884000143__31122025__598255a0.xlsx
│       │   ├── VIBRA ENERGIA RATING 06112025__5e6d60f2.xlsx
│       │   ├── VIBRA ENERGIA RATING 06112025__padrao_7__25369840000157__31122024__5e6d60f2.xlsx
│       │   ├── Vitol 04062025__d830b369.xlsx
│       │   ├── Vitol 04062025__padrao_3__43308969000137__31122024__d830b369.xlsx
│       │   ├── VITOL 05062026__4b3aad48.xlsx
│       │   ├── VITOL 05062026__padrao_6__43308969000137__31122025__4b3aad48.xlsx
│       │   ├── Vitol 27032026 df 2025__dabf5ea1.xlsx
│       │   ├── Vitol 27032026 df 2025__padrao_6__43308969000137__31122024__dabf5ea1.xlsx
│       │   ├── VITOL 30 04 2024__7668c33e.xlsx
│       │   ├── VITOL 30 04 2024__padrao_6__43308969000137__31122023__7668c33e.xlsx
│       │   ├── VITOL POWER 20072026__af212072.xlsx
│       │   ├── VITOL POWER 20072026__padrao_6__43308969000137__31122025__af212072.xlsx
│       │   ├── Vitol Power Brasil__e7dc85e6.xlsx
│       │   ├── Vitol Power Brasil__padrao_2__43308969000137__30062022__e7dc85e6.xlsx
│       │   ├── VIVAZ ENERGIA 15_06_2022__f3bbdbe1.xlsx
│       │   ├── VIVAZ ENERGIA 15_06_2022__padrao_2__26537119000191__31122021__f3bbdbe1.xlsx
│       │   ├── VIX 17_11_2021__433405d4.xlsx
│       │   ├── VIX 17_11_2021__padrao_2__30206620000142__31122020__433405d4.xlsx
│       │   ├── VOLTALIA (GRUPO) 24_08_2022__e8794653.xlsx
│       │   ├── VOLTALIA RATING 06112025__137b7dcf.xlsx
│       │   ├── VOLTALIA RATING 06112025__padrao_7__29350168000109__31122024__137b7dcf.xlsx
│       │   ├── VOLTALIA_2024__1361c8fd.xlsx
│       │   ├── VOLTALIA_2024__padrao_3__29350168000109__31122024__1361c8fd.xlsx
│       │   ├── VOTENER (GRUPO)_14_10_2021__3fd8d8c0.xlsx
│       │   ├── VOTENER_09_06_2021__7a3234d8.xlsx
│       │   ├── VOTENER_09_06_2021__padrao_2__03984862000194__31122020__7a3234d8.xlsx
│       │   ├── W7_25_05_2021__07017edc.xlsx
│       │   ├── W7_25_05_2021__padrao_2__32783106000103__31122020__07017edc.xlsx
│       │   ├── WD AGROINDUSTRIAL 13072026__5d08213f.xlsx
│       │   ├── WD AGROINDUSTRIAL 13072026__padrao_6__01105558000102__31122025__5d08213f.xlsx
│       │   ├── WORLDSE_20.06.2024__b968a36b.xlsx
│       │   ├── WORLDSE_20.06.2024__padrao_6__28423185000166__31122023__b968a36b.xlsx
│       │   ├── WX ENERGIA(RAIZEN)_04.07.2024__2ad8e513.xlsx
│       │   ├── WX ENERGIA(RAIZEN)_04.07.2024__padrao_3__13777004000122__31122023__2ad8e513.xlsx
│       │   ├── WX ENERGY_10_09_2021__cf9a5a92.xlsx
│       │   ├── WX ENERGY_10_09_2021__padrao_2__13777004000122__31032020__cf9a5a92.xlsx
│       │   ├── WXE - RAÍZEN 25082023__2872b114.xlsx
│       │   ├── WXE - RAÍZEN 25082023__padrao_3__13777004000122__31122022__2872b114.xlsx
│       │   ├── XP 05092025__17d483e4.xlsx
│       │   ├── XP 05092025__padrao_3__34475373000130__31122024__17d483e4.xlsx
│       │   ├── XP 19052025__9cfed231.xlsx
│       │   ├── XP 19052025__padrao_3__34475373000130__31122024__9cfed231.xlsx
│       │   ├── XP COM 17072026__cb90f295.xlsx
│       │   ├── XP COM 17072026__padrao_6__34475373000130__31122025__cb90f295.xlsx
│       │   ├── XP COMERCIALIZADORA 14_07_2022__c0fbf2dc.xlsx
│       │   ├── XP COMERCIALIZADORA 14_07_2022__padrao_2__34475373000130__31122021__c0fbf2dc.xlsx
│       │   ├── XP RATING 13112025__f6e07856.xlsx
│       │   ├── XP RATING 13112025__padrao_7__34475373000130__31122024__f6e07856.xlsx
│       │   ├── XP_03112023__cc88b058.xlsx
│       │   ├── XP_03112023__padrao_3__34475373000130__31122022__cc88b058.xlsx
│       │   ├── XP_06_09_2021__4e555fde.xlsx
│       │   ├── XP_06_09_2021__padrao_2__34475373000130__30062021__4e555fde.xlsx
│       │   ├── ZEST 15042024__dbff0ddf.xlsx
│       │   ├── ZEST 15042024__padrao_6__35487170000127__31122023__dbff0ddf.xlsx
│       │   ├── ZEST 27062025__f333d559.xlsx
│       │   ├── ZEST 27062025__padrao_3__35487170000127__31122024__f333d559.xlsx
│       │   ├── ZEST _05_05_2021(modelo novo)__d923a06b.xlsx
│       │   ├── ZEST _05_05_2021(modelo novo)__padrao_2__35487170000127__31122020__d923a06b.xlsx
│       │   ├── ZEST_26_04_2022__c65c9b88.xlsx
│       │   ├── ZEST_26_04_2022__padrao_2__35487170000127__31122021__c65c9b88.xlsx
│       │   ├── ZETA 18_04_2022__b4b1f5ab.xlsx
│       │   ├── ZETA 18_04_2022__padrao_2__17386017000121__31122021__b4b1f5ab.xlsx
│       │   ├── ZETA Energia_16_06_2021__f7525be6.xlsx
│       │   ├── ZETA Energia_16_06_2021__padrao_2__17386017000121__31122020__f7525be6.xlsx
│       │   └── ZETA_17032023__26e46e5b.xlsx
│       └── fichas_consumidores/
│           ├── 3R PETROLEUM  22042024__29e292f7.xlsx
│           ├── 3R PETROLEUM  22042024__padrao_1__12091809000155__31122023__29e292f7.xlsx
│           ├── 3R PETROLEUM 13082025__7004cc19.xlsx
│           ├── 3R PETROLEUM 13082025__padrao_1__12091809000155__31122024__7004cc19.xlsx
│           ├── 3R PETROLEUM RATING 19112025__b29c43ea.xlsx
│           ├── A 100 ROW Serviços de Dados 10082023__69cb53ad.xlsx
│           ├── A 100 ROW Serviços de Dados 10082023__padrao_1__12147176000150__31122022__69cb53ad.xlsx
│           ├── ACO CEARENSE RATING 07012026__c42f0857.xlsx
│           ├── ACO CEARENSE RATING 07012026__padrao_2__00990842000138__31122024__c42f0857.xlsx
│           ├── ACUCAREIRA ZILOR 27032026__23a04d4c.xlsx
│           ├── ACUCAREIRA ZILOR 27032026__padrao_2__60855574000173__31032025__23a04d4c.xlsx
│           ├── ADECOAGRO 10042026__5961e33e.xlsx
│           ├── ADECOAGRO 10042026__padrao_2__07903169000109__31122025__5961e33e.xlsx
│           ├── AEBES HEJSN 01122023__ce751321.xlsx
│           ├── AEBES HEJSN 01122023__padrao_1__28127926000242__31122022__ce751321.xlsx
│           ├── AEGEA 17072025__c7c029c3.xlsx
│           ├── AEGEA 17072025__padrao_1__42644220000106__31122024__c7c029c3.xlsx
│           ├── AEGEA 20-07-2022__12dedf77.xlsx
│           ├── AEGEA 20-07-2022__padrao_1__08827501000158__31122021__12dedf77.xlsx
│           ├── AEGEA RATING 09122025__8983ea91.xlsx
│           ├── AEGEA SANEAMENTO 23072026__75a31198.xlsx
│           ├── AEGEA SANEAMENTO 23072026__padrao_3__08827501000158__31032026__75a31198.xlsx
│           ├── AEGEA_RIO4_16122024__2c3abd4b.xlsx
│           ├── AEGEA_RIO4_16122024__padrao_1__42644220000106__31122023__2c3abd4b.xlsx
│           ├── Aeroporto Confins 25032025__6664881c.xlsx
│           ├── Aeroporto Confins 25032025__padrao_1__19674909000153__31122024__6664881c.xlsx
│           ├── AEROPORTO DE GUARULHOS 28082025__7db2b456.xlsx
│           ├── AEROPORTO DE GUARULHOS 28082025__padrao_1__15578569000106__31122024__7db2b456.xlsx
│           ├── AEROPORTO DE GUARULHOS 28082025_consiste__19aa1d6e.xlsx
│           ├── AEROPORTO DE GUARULHOS RATING 04112025__bda732d0.xlsx
│           ├── AEROPORTOS DO NORDESTE_16032023__3e497721.xlsx
│           ├── AEROPORTOS DO NORDESTE_16032023__padrao_1__33919741000120__31122021__3e497721.xlsx
│           ├── AGRONORTE RATING 02032026__9aa0e395.xlsx
│           ├── AGRONORTE RATING 02032026__padrao_2__03503798000182__31122024__9aa0e395.xlsx
│           ├── AGROPÉU 18062025__e3b1ff6d.xlsx
│           ├── AGROPÉU 18062025__padrao_1__16617789000164__31122024__e3b1ff6d.xlsx
│           ├── AGUAS DO RIO 4__d499c24e.xlsx
│           ├── AGUAS DO RIO 4__padrao_3__42644220000106__31122025__d499c24e.xlsx
│           ├── AHLSTROM-MUNKSJO 27052026__dfe0ef31.xlsx
│           ├── AHLSTROM-MUNKSJO 27052026__padrao_2__00767144000178__31122025__dfe0ef31.xlsx
│           ├── AIR LIQUIDE 06072026__a51b4719.xlsx
│           ├── ALBRAS 21072026__793114a9.xlsx
│           ├── ALBRAS 21072026__padrao_3__05053020000144__31122025__793114a9.xlsx
│           ├── ALBRAS 27052025__562665da.xlsx
│           ├── ALBRAS 27052025__padrao_1__05053020000144__31122024__562665da.xlsx
│           ├── ALBRAS RATING 05012026__d81a04f6.xlsx
│           ├── ALCOA 08042026__c962acb8.xlsx
│           ├── ALCOA 08042026__padrao_2__23637697000101__31122025__c962acb8.xlsx
│           ├── ALCOA ALUMINIO 30052025__bed80a90.xlsx
│           ├── ALCOA ALUMINIO 30052025__padrao_1__23637697000101__31122024__bed80a90.xlsx
│           ├── ALCOA ALUMINIO RATING 01122025__a6f6b447.xlsx
│           ├── ALCOA WORLD 13052026__c2ec63c5.xlsx
│           ├── ALCOESTE BIOENERTIA 04-05-2026__308b90b9.xlsx
│           ├── ALCOESTE BIOENERTIA 04-05-2026__padrao_2__43545284000104__31122024__308b90b9.xlsx
│           ├── ALCOESTE FERNANDÓPOLIS 22052026__08570b90.xlsx
│           ├── ALCOESTE FERNANDÓPOLIS 22052026__padrao_2__43545284000104__31122025__08570b90.xlsx
│           ├── ALIANSCE SONAE_29062023__5cd43bc6.xlsx
│           ├── ALIANSCE SONAE_29062023__padrao_1__05878397000132__31122022__5cd43bc6.xlsx
│           ├── ALIANÇA GERAÇÃO 17072025__7094c94e.xlsx
│           ├── ALIANÇA GERAÇÃO 17072025__padrao_1__12009135000105__31122024__7094c94e.xlsx
│           ├── ALIANÇA GERAÇÃO RATING 28012026__35513ff1.xlsx
│           ├── ALLIANCE RATING 04022025__472e95b7.xlsx
│           ├── ALLIANCE RATING 04022025__padrao_2__05297665000122__31122025__472e95b7.xlsx
│           ├── ALUNORTE 17062026__9a710d26.xlsx
│           ├── ALUNORTE 17062026__padrao_3__05848387000154__31122025__9a710d26.xlsx
│           ├── ALUNORTE RATING 18122025__27be07f2.xlsx
│           ├── ALUNORTE RATING 18122025__padrao_2__05848387000154__31122024__27be07f2.xlsx
│           ├── AMBIENTAL - NESTOR DE BARROS 31072026__eed6be54.xlsx
│           ├── AMBIENTAL - NESTOR DE BARROS 31072026__padrao_3__08405256000190__31122025__eed6be54.xlsx
│           ├── AMELPLAST RATING 29012026__5e23a5af.xlsx
│           ├── AMELPLAST RATING 29012026__padrao_2__40797554000186__31122024__5e23a5af.xlsx
│           ├── Anglo Amercia 27022024 v2__7480ff57.xlsx
│           ├── Anglo Amercia 27022024 v2__padrao_1__42184226001969__31122022__7480ff57.xlsx
│           ├── Anglo Amercia 27022024__640fff72.xlsx
│           ├── Anglo Amercia 27022024__padrao_1__02359572000430__31122022__640fff72.xlsx
│           ├── ANGLO AMERICAN 03072026__105986a0.xlsx
│           ├── ANGLO AMERICAN 03072026__padrao_3__42184226000130__31122025__105986a0.xlsx
│           ├── ANGLO AMERICAN 31.12.2023__24a19249.xlsx
│           ├── ANGLO AMERICAN 31.12.2023__padrao_1__42184226001969__31122023__24a19249.xlsx
│           ├── ANGLO AMERICAN RATING 14102025__14c44b45.xlsx
│           ├── ANGLO AMERICAN RATING 14102025__padrao_2__02359572000430__31122024__14c44b45.xlsx
│           ├── APERAM RATING 18032026__acaef2e6.xlsx
│           ├── APERAM RATING 18032026__padrao_2__33390170000189__31122024__acaef2e6.xlsx
│           ├── ARAMART 28072026__f1d7f510.xlsx
│           ├── ARAMART 28072026__padrao_3__13416922000126__31122025__f1d7f510.xlsx
│           ├── ARAUCO - 27032025__afbadae0.xlsx
│           ├── ARAUCO - 27032025__padrao_1__47658073000139__31122024__afbadae0.xlsx
│           ├── ARCELORMITTAL - 00350481__4142ab15.xlsx
│           ├── ARCELORMITTAL - 00350481__padrao_1__09509535000167__31122024__4142ab15.xlsx
│           ├── ARCELORMITTAL 13052026__f7f419c2.xlsx
│           ├── ARCELORMITTAL 13052026__padrao_2__17469701000177__31122025__f7f419c2.xlsx
│           ├── ARCELORMITTAL PECEM 17072026__31a7704d.xlsx
│           ├── ARCELORMITTAL RATING 05112025__c02ec233.xlsx
│           ├── ARCELORMITTAL RATING 05112025__padrao_2__17469701000177__31122024__c02ec233.xlsx
│           ├── Ardagh Metal 26_09_2022__71a4659b.xlsx
│           ├── Ardagh Metal 26_09_2022__padrao_1__24168115000158__31122021__71a4659b.xlsx
│           ├── ARLANXEO_21032023__a5dbc7c4.xlsx
│           ├── ARLANXEO_21032023__padrao_1__29667227000177__31122021__a5dbc7c4.xlsx
│           ├── ASCENTY 09072025__d4b664d0.xlsx
│           ├── ASCENTY 09072025__padrao_1__13743550000142__31122024__d4b664d0.xlsx
│           ├── ASCENTY 21052026__78981805.xlsx
│           ├── ASCENTY 21052026__padrao_2__13743550000142__31122025__78981805.xlsx
│           ├── ASCENTY RATING 13102023__88a12623.xlsx
│           ├── ASCENTY RATING 13102023__padrao_2__13743550000142__88a12623.xlsx
│           ├── ASSAI ATACADISTA 25.07.2024__5f4444b1.xlsx
│           ├── ASSAI ATACADISTA 25.07.2024__padrao_1__06057223000171__31122023__5f4444b1.xlsx
│           ├── ASSAI RATING 09032026__f92a308e.xlsx
│           ├── ASSAI RATING 09032026__padrao_2__06057223000171__31122025__f92a308e.xlsx
│           ├── Assaí atacadista 25032025__be9cf5ba.xlsx
│           ├── Assaí atacadista 25032025__padrao_1__06057223000171__31122024__be9cf5ba.xlsx
│           ├── Assaí Atacadista_24072023__d186ca09.xlsx
│           ├── Assaí Atacadista_24072023__padrao_1__06057223000171__31122022__d186ca09.xlsx
│           ├── Associação do Hospital de Jaragiuá - Ava__5add7876.xlsx
│           ├── Associação do Hospital de Jaragiuá - Ava__padrao_1__39913479000192__31122021__5add7876.xlsx
│           ├── Associação Hospitalar Santana - Avaliaçã__710675af.xlsx
│           ├── Associação Hospitalar Santana - Avaliaçã__padrao_1__15186359000172__31122021__710675af.xlsx
│           ├── ASUN RATING 24102025__3a856968.xlsx
│           ├── ASUN RATING 24102025__padrao_2__92091891000157__3a856968.xlsx
│           ├── ATVOS BIOENERGIA BRENCO RATING 22122025__1fa506bb.xlsx
│           ├── ATVOS BIOENERGIA BRENCO RATING 22122025__padrao_2__08070566000100__31032025__1fa506bb.xlsx
│           ├── ATVOS BIOENERGIA CONQUISTA DO PONTAL RAT__ef630b1e.xlsx
│           ├── ATVOS BIOENERGIA CONQUISTA DO PONTAL RAT__padrao_2__07298800000180__31032025__ef630b1e.xlsx
│           ├── ATVOS BIOENERGIA ELDORADO RATING 2212202__614031e7.xlsx
│           ├── ATVOS BIOENERGIA ELDORADO RATING 2212202__padrao_2__05620523000154__31032025__614031e7.xlsx
│           ├── ATVOS BIOENERGIA RIO CLARO RATING 231220__49e65286.xlsx
│           ├── ATVOS BIOENERGIA RIO CLARO RATING 231220__padrao_2__08598391000108__49e65286.xlsx
│           ├── ATVOS BIOENERGIA SANTA LUZIA__f811a679.xlsx
│           ├── ATVOS BIOENERGIA SANTA LUZIA__padrao_2__08906558000142__31122025__f811a679.xlsx
│           ├── AURORA 10082023__b9308554.xlsx
│           ├── AURORA 10082023__padrao_1__83310441000117__31122022__b9308554.xlsx
│           ├── AURORA ALIMENTOS 20072026__6ca5d965.xlsx
│           ├── AURORA ALIMENTOS 20072026__padrao_3__83310441000117__31122025__6ca5d965.xlsx
│           ├── AUTODROMO ENERGÉTICA 13062025__bc709411.xlsx
│           ├── AUTODROMO ENERGÉTICA 13062025__padrao_1__07647793000184__31122024__bc709411.xlsx
│           ├── AVENORTE_20092023__f4cdd710.xlsx
│           ├── AVENORTE_20092023__padrao_1__01682147000171__31122023__f4cdd710.xlsx
│           ├── AVENORTE_30062023__c60f6f10.xlsx
│           ├── AVENORTE_30062023__padrao_1__01682147000171__31122022__c60f6f10.xlsx
│           ├── BALL_02032023__ad9e787e.xlsx
│           ├── BALL_02032023__padrao_1__00771979000100__31122021__ad9e787e.xlsx
│           ├── BASF 14072026__9e857d60.xlsx
│           ├── BASF 14072026__padrao_3__48539407000118__31122025__9e857d60.xlsx
│           ├── BASF 23062026__b268e14e.xlsx
│           ├── BASF 25082025__3b04d6c2.xlsx
│           ├── BASF 25082025__padrao_1__48539407000118__31122024__3b04d6c2.xlsx
│           ├── BASF RATING 14102025__1c474f3e.xlsx
│           ├── BASF RATING 14102025__padrao_2__48539407000118__1c474f3e.xlsx
│           ├── BE8 RATING 11122025__77452d9c.xlsx
│           ├── BE8 RATING 11122025__padrao_2__07322382000119__31122024__77452d9c.xlsx
│           ├── BE8_26_08_2024__04773119.xlsx
│           ├── BE8_26_08_2024__padrao_1__07322382000119__31122023__04773119.xlsx
│           ├── BELLO_01062023__7538c0bf.xlsx
│           ├── BELLO_01062023__padrao_1__08201770000104__31122022__7538c0bf.xlsx
│           ├── BERNECK 03072025__320a78ac.xlsx
│           ├── BERNECK 03072025__padrao_1__81905176000194__31122024__320a78ac.xlsx
│           ├── BERNECK 08102025__6e0a6a6c.xlsx
│           ├── BERNECK 08102025__padrao_2__81905176000194__6e0a6a6c.xlsx
│           ├── Bimbo_02_09_2024__231c7f61.xlsx
│           ├── Bimbo_02_09_2024__padrao_1__35402759000185__31122023__231c7f61.xlsx
│           ├── Bioagri Laboratórios_03-10-2022__dc2cc2a7.xlsx
│           ├── Bioagri Laboratórios_03-10-2022__padrao_1__62473004000144__31122021__dc2cc2a7.xlsx
│           ├── BIOENERGIA BARRA_30062023__287dcdcd.xlsx
│           ├── BIOENERGIA BARRA_30062023__padrao_1__18788137000118__31122021__287dcdcd.xlsx
│           ├── BIOHOSP 15072026__a871e09a.xlsx
│           ├── BIOHOSP 15072026__padrao_3__18269125000187__31122025__a871e09a.xlsx
│           ├── BIORIGIN 15072026__233627cf.xlsx
│           ├── BIORIGIN 15072026__padrao_3__53162783000176__31122025__233627cf.xlsx
│           ├── BO PAPER 02062026__f48fa7b7.xlsx
│           ├── BO PAPER 02062026__padrao_2__07632665000167__31122025__f48fa7b7.xlsx
│           ├── BO Paper 04_05_2022__5bdc5b5e.xlsx
│           ├── BO Paper 04_05_2022__padrao_1__07632665000167__31122021__5bdc5b5e.xlsx
│           ├── BO PAPER RATING 13102025__96df73e7.xlsx
│           ├── BO PAPER RATING 13102025__padrao_2__07632665000167__31122024__96df73e7.xlsx
│           ├── BOA FÉ ENERGÉTICA 12062025__16ecdff7.xlsx
│           ├── BOA FÉ ENERGÉTICA 12062025__padrao_1__07647780000105__31122024__16ecdff7.xlsx
│           ├── BOPAPER_2023_05_11__bbe9d998.xlsx
│           ├── BOPAPER_2023_05_11__padrao_1__07632665000167__31122022__bbe9d998.xlsx
│           ├── BOZEL 24062026__c1a69f33.xlsx
│           ├── BOZEL 24062026__padrao_3__08090788000267__31122025__c1a69f33.xlsx
│           ├── BOZEL BRASIL 21082025__61615589.xlsx
│           ├── BOZEL BRASIL 21082025__padrao_1__08090788000267__31122024__61615589.xlsx
│           ├── BOZEL RATING 31102025__7ac06025.xlsx
│           ├── BRACELL CELULOSE 04082025__c4d2dd4f.xlsx
│           ├── BRACELL CELULOSE 04082025__padrao_1__53943098000187__31122024__c4d2dd4f.xlsx
│           ├── BRACELL RATING 02122025__1d88e0e2.xlsx
│           ├── BRACELL RATING 10032025__b25e2154.xlsx
│           ├── BRADESCO_21_02_2022__3c7c8a21.xlsx
│           ├── BRADESCO_21_02_2022__padrao_1__60746948000112__31122021__3c7c8a21.xlsx
│           ├── BRANCO PERES 04052026__17cffb1e.xlsx
│           ├── BRANCO PERES 04052026__padrao_2__43619832001760__31122024__17cffb1e.xlsx
│           ├── BRASFRIGO 15062026__6798207a.xlsx
│           ├── BRASFRIGO 15062026__padrao_3__19166180000104__31122025__6798207a.xlsx
│           ├── Brasil Tropical 13072023__3a5721a3.xlsx
│           ├── Brasil Tropical 13072023__padrao_1__17210843000115__31122022__3a5721a3.xlsx
│           ├── BRASKEM - 05 04 2024__d2f5377c.xlsx
│           ├── BRASKEM - 05 04 2024__padrao_1__42150391000170__31122023__d2f5377c.xlsx
│           ├── BRASKEM 21052026__920e1508.xlsx
│           ├── BRASKEM 21052026__padrao_2__42150391000170__31122025__920e1508.xlsx
│           ├── BRASKEM 22072025__d30e969b.xlsx
│           ├── BRASKEM 22072025__padrao_1__42150391000170__31122024__d30e969b.xlsx
│           ├── BRASKEM RATING 24102025__685afd60.xlsx
│           ├── Brasken 01022024 sem eprotocolo__e46bb666.xlsx
│           ├── Brasken 01022024 sem eprotocolo__padrao_1__42150391000170__31122022__e46bb666.xlsx
│           ├── Brastex - Avaliação Middle__42c15430.xlsx
│           ├── Brastex - Avaliação Middle__padrao_1__87547170000179__31122021__42c15430.xlsx
│           ├── Brastex 10062024__cf1ecf94.xlsx
│           ├── Brastex 10062024__padrao_1__09258807000101__31122023__cf1ecf94.xlsx
│           ├── BRASTEX RATING 08012026__7b1f02c5.xlsx
│           ├── BRASTEX RATING 08012026__padrao_2__09258807000101__31122024__7b1f02c5.xlsx
│           ├── Braswell__ba08c86c.xlsx
│           ├── Braswell__padrao_1__11778932000186__31122021__ba08c86c.xlsx
│           ├── BRAVA 15052026__71c3017b.xlsx
│           ├── BRAVA 15052026__padrao_2__12091809000155__31122025__71c3017b.xlsx
│           ├── BRAVOX_31072023__12277e4a.xlsx
│           ├── BRAVOX_31072023__padrao_1__60854833000141__31122022__12277e4a.xlsx
│           ├── BRF 12082024__a525427f.xlsx
│           ├── BRF 12082024__padrao_1__01838723000127__31122023__a525427f.xlsx
│           ├── BRF FOODS 22072025__b2de4d00.xlsx
│           ├── BRF FOODS 22072025__padrao_1__01838723000127__31122024__b2de4d00.xlsx
│           ├── BRF RATING 01122025__73f5155c.xlsx
│           ├── BRF RATING 01122025__padrao_2__01838723000127__31122025__73f5155c.xlsx
│           ├── Bridgestone do Brasil__e6b92ba9.xlsx
│           ├── Bridgestone do Brasil__padrao_1__57497539000115__31122021__e6b92ba9.xlsx
│           ├── Bridgestone_24_08_2022 - 2__67726dd5.xlsx
│           ├── Bridgestone_24_08_2022 - 2__padrao_1__57497539000700__31122021__67726dd5.xlsx
│           ├── Bridgestone_24_08_2022 - 3__72e46536.xlsx
│           ├── Bridgestone_24_08_2022 - 3__padrao_1__57497539001600__31122021__72e46536.xlsx
│           ├── Bridgestone_24_08_2022 - 4__4a810282.xlsx
│           ├── Bridgestone_24_08_2022 - 4__padrao_1__57497539001359__31122021__4a810282.xlsx
│           ├── BRK Ambiental - Avaliação Middle__211c4cd3.xlsx
│           ├── BRK Ambiental - Avaliação Middle__padrao_1__24396489000120__31122021__211c4cd3.xlsx
│           ├── BUNGE 09102025__e9800550.xlsx
│           ├── BUNGE 09102025__padrao_2__84046101000193__e9800550.xlsx
│           ├── BUNGE 18062026__d1fcb09a.xlsx
│           ├── BUNGE 18062026__padrao_3__84046101000193__31122025__d1fcb09a.xlsx
│           ├── C. VALE 25052026__7eea2bb3.xlsx
│           ├── C. VALE 25052026__padrao_2__77863223017930__31122025__7eea2bb3.xlsx
│           ├── C. VALE RATING 07112025__efc27454.xlsx
│           ├── C. VALE RATING 07112025__padrao_2__77863223004366__31122024__efc27454.xlsx
│           ├── CAERN_23042025__cc258eef.xlsx
│           ├── CAERN_23042025__padrao_1__08334385000135__31122024__cc258eef.xlsx
│           ├── CAESB RATING 20012026__af170b8a.xlsx
│           ├── CAESB RATING 20012026__padrao_2__00082024000137__31122024__af170b8a.xlsx
│           ├── CAMPO BELO G1 CARLOS CALDEIRA 30072026__7b724c22.xlsx
│           ├── CAMPO BELO G1 CARLOS CALDEIRA 30072026__padrao_3__01832301000144__31122025__7b724c22.xlsx
│           ├── CANDEIAS 15102025__c44589cb.xlsx
│           ├── CANDEIAS 15102025__padrao_2__43446434000122__c44589cb.xlsx
│           ├── CANOINHAS 17072025__2e26b796.xlsx
│           ├── CANOINHAS 17072025__padrao_1__76827344000130__31122024__2e26b796.xlsx
│           ├── Caramuru 2022-07-18__0202636e.xlsx
│           ├── Caramuru 2022-07-18__padrao_1__00080671000100__31122021__0202636e.xlsx
│           ├── Cargil 05.08.2024__026482d6.xlsx
│           ├── Cargil 05.08.2024__padrao_1__01961898000127__31122023__026482d6.xlsx
│           ├── Cargil 28022024__9733cb32.xlsx
│           ├── Cargil 28022024__padrao_1__01961898000127__31122022__9733cb32.xlsx
│           ├── CARGILL 11062026 - REVISÃO__5a32ff1f.xlsx
│           ├── CARGILL 11062026 - REVISÃO__padrao_3__60498706000157__31122025__5a32ff1f.xlsx
│           ├── CARGILL 15072025__006dd374.xlsx
│           ├── CARGILL 15072025__padrao_1__60498706000157__31122024__006dd374.xlsx
│           ├── CARGILL RATING 13102025__b0d7ca82.xlsx
│           ├── CARGILL RATING 13102025__padrao_2__60498706000157__b0d7ca82.xlsx
│           ├── CBA - Cia Brasileira de Alumínio 2022-07__c172740c.xlsx
│           ├── CBA - Cia Brasileira de Alumínio 2022-07__padrao_1__61409892000920__31122021__c172740c.xlsx
│           ├── CBA 08102025 RATING RETIFICADO__bf5ce995.xlsx
│           ├── CBA 08102025 RATING RETIFICADO__padrao_2__61409892000173__bf5ce995.xlsx
│           ├── CBA 08102025__c4591776.xlsx
│           ├── CBA 08102025__padrao_2__61409892000173__c4591776.xlsx
│           ├── CBA 24062026__1c7d407b.xlsx
│           ├── CBA 24062026__padrao_3__61409892000173__31122025__1c7d407b.xlsx
│           ├── CBA CIA BRASILEIRA DE ALUMINIO 30052025__292acfa3.xlsx
│           ├── CEDAE_23082023__d872e0c3.xlsx
│           ├── CEDAE_23082023__padrao_1__33352394000104__31122022__d872e0c3.xlsx
│           ├── CEEE RATING 02122025__6bfe593b.xlsx
│           ├── CEEE RATING 02122025__padrao_2__39881421000104__31122024__6bfe593b.xlsx
│           ├── CEEE-G_02_06_2025__648c1e0d.xlsx
│           ├── CEEE-G_02_06_2025__padrao_1__39881421000104__31122025__648c1e0d.xlsx
│           ├── CEESAM 11-12-2025__67ab82b3.xlsx
│           ├── CEESAM 11-12-2025__padrao_2__85937316000167__31122024__67ab82b3.xlsx
│           ├── CELETRO 08072026__cdacef6e.xlsx
│           ├── CELETRO 08072026__padrao_3__87776043000141__31122025__cdacef6e.xlsx
│           ├── Centrais Eólicas de Caetité Participaçõe__d1aaaba7.xlsx
│           ├── Centrais Eólicas de Caetité Participaçõe__padrao_2__09341337000137__31122023__d1aaaba7.xlsx
│           ├── CENTRAL PACK 24082023__7f6022a2.xlsx
│           ├── CENTRAL PACK 24082023__padrao_1__07227026000116__31122022__7f6022a2.xlsx
│           ├── CEPASA 08072025__c9708129.xlsx
│           ├── CEPASA 08072025__padrao_1__13348048000137__31122024__c9708129.xlsx
│           ├── CEPASA RATING 19112025__8fd3b362.xlsx
│           ├── Ceramica_Formigres_18_01_2022__fb96e543.xlsx
│           ├── Ceramica_Formigres_18_01_2022__padrao_1__01325023000139__31122020__fb96e543.xlsx
│           ├── CERMISSOES 17082026__2dfffde5.xlsx
│           ├── CERMISSOES 17082026__padrao_3__97081434000103__31122025__2dfffde5.xlsx
│           ├── CERTAJA 12082026__24d1f334.xlsx
│           ├── CERTAJA 12082026__padrao_3__97839922000129__31122025__24d1f334.xlsx
│           ├── CERTHIL 17082026__16197e42.xlsx
│           ├── CERTHIL 17082026__padrao_3__98042963000152__31122025__16197e42.xlsx
│           ├── CERÂMICA ELISABETH__610a9852.xlsx
│           ├── CERÂMICA ELISABETH__padrao_1__08944802000161__31122020__610a9852.xlsx
│           ├── Cessão Flexoprint para All4Labels__d16e4967.xlsx
│           ├── Cessão Flexoprint para All4Labels__padrao_1__21399573000100__31122021__d16e4967.xlsx
│           ├── CIA Sulamericana de Distribuição sem epr__dd3fbe3b.xlsx
│           ├── CIA Sulamericana de Distribuição sem epr__padrao_1__11517841000197__31122022__dd3fbe3b.xlsx
│           ├── Cimento Campeão Alvorada_14_01_2022__7cfb4cce.xlsx
│           ├── Cimento Campeão Alvorada_14_01_2022__padrao_1__07957149000102__31122020__7cfb4cce.xlsx
│           ├── CIMENTO ITAMBE 27_07_2022__ca039cd0.xlsx
│           ├── CIMENTO ITAMBE 27_07_2022__padrao_1__76630573000160__31122021__ca039cd0.xlsx
│           ├── CISER 11092025__039e81e8.xlsx
│           ├── CISER 11092025__padrao_1__84709955000102__31122024__039e81e8.xlsx
│           ├── CITROSUCO_10042025__f5c8c50c.xlsx
│           ├── CITROSUCO_10042025__padrao_1__33010786000187__31122024__f5c8c50c.xlsx
│           ├── CJ DO BRASIL 01072026__58cc677f.xlsx
│           ├── CJ DO BRASIL 01072026__padrao_3__07450031000193__31122025__58cc677f.xlsx
│           ├── CJ do Brasil_13042023__5be760b6.xlsx
│           ├── CJ do Brasil_13042023__padrao_1__07450031000193__31122021__5be760b6.xlsx
│           ├── CLUBE CURITIBANO 06052026__7d13fd21.xlsx
│           ├── CLUBE CURITIBANO 06052026__padrao_2__76493626000149__31102025__7d13fd21.xlsx
│           ├── CMPC 14072026__facbd799.xlsx
│           ├── COAMO 02062025__0eda9770.xlsx
│           ├── COAMO 02062025__padrao_1__75904383000121__31122024__0eda9770.xlsx
│           ├── COAMO 11012024__a6ce8adf.xlsx
│           ├── COAMO 11012024__padrao_1__75904383000121__31122022__a6ce8adf.xlsx
│           ├── COASUL RATING 31102025__f81d96ad.xlsx
│           ├── COASUL RATING 31102025__padrao_2__79863569000130__31122024__f81d96ad.xlsx
│           ├── Coca-cola FEMSA 05032024__5e08b655.xlsx
│           ├── Coca-cola FEMSA 05032024__padrao_1__61186888000193__5e08b655.xlsx
│           ├── COCA-COLA FEMSA RATING 25032026__60dcf530.xlsx
│           ├── COCA-COLA FEMSA RATING 25032026__padrao_2__61186888000193__31032025__60dcf530.xlsx
│           ├── Cocamar 01022024 sem eprotocolo__f8455706.xlsx
│           ├── Cocamar 01022024 sem eprotocolo__padrao_1__79114450000165__31122022__f8455706.xlsx
│           ├── COCAMAR 11012024__7e1bfc50.xlsx
│           ├── COCAMAR 11012024__padrao_1__79114450001480__31122022__7e1bfc50.xlsx
│           ├── COCAMAR 27-04-2026__bea30380.xlsx
│           ├── COCAMAR 27-04-2026__padrao_2__79114450000165__31122025__bea30380.xlsx
│           ├── Cocamar 28022024__708fb770.xlsx
│           ├── Cocamar 28022024__padrao_1__79114450000165__31122023__708fb770.xlsx
│           ├── COFCO 16042026__d8eec9e7.xlsx
│           ├── COFCO 16042026__padrao_2__06315338000119__31122024__d8eec9e7.xlsx
│           ├── COFCO 21072026__047ef85e.xlsx
│           ├── COFCO 21072026__padrao_3__06315338000119__31122025__047ef85e.xlsx
│           ├── COLGATE 24042025__2062e4f2.xlsx
│           ├── COLGATE 24042025__padrao_1__03816532000190__31122024__2062e4f2.xlsx
│           ├── Companhia Aguas de Joinville - Avaliação__0b1be501.xlsx
│           ├── Companhia Aguas de Joinville - Avaliação__padrao_1__07226794000155__31122021__0b1be501.xlsx
│           ├── COMPANHIA DE CIMENTO CAMPEAO ALVORADA RA__a9cb11bf.xlsx
│           ├── COMPANHIA DE CIMENTO CAMPEAO ALVORADA RA__padrao_2__21109697000103__31122024__a9cb11bf.xlsx
│           ├── COMPANHIA RIOGRANDENSE DE SANEAMENTO 180__4afe409f.xlsx
│           ├── COMPANHIA RIOGRANDENSE DE SANEAMENTO 180__b6ac098d.xlsx
│           ├── COMPANHIA RIOGRANDENSE DE SANEAMENTO 180__padrao_1__92802784000190__31122024__4afe409f.xlsx
│           ├── COMPANHIA RIOGRANDENSE DE SANEAMENTO 191__0a89ce64.xlsx
│           ├── COMUSA 05072024__dcc2d01d.xlsx
│           ├── COMUSA 05072024__padrao_1__09509569000151__31122023__dcc2d01d.xlsx
│           ├── CONSORCIO TRANSVIDA RATING 18022026__a829a697.xlsx
│           ├── Continental Camaçari_21_02_2022__f3e60e98.xlsx
│           ├── Continental Camaçari_21_02_2022__padrao_1__02036483000614__31122020__f3e60e98.xlsx
│           ├── CONTINENTAL_15072024__05cff9a8.xlsx
│           ├── CONTINENTAL_15072024__padrao_1__03650060000148__31122023__05cff9a8.xlsx
│           ├── CONTINENTAL_15072024_V1__01eb0779.xlsx
│           ├── CONTINENTAL_15072024_V1__padrao_1__02036483000614__31122023__01eb0779.xlsx
│           ├── COOPAVEL 11012024__e5e5322d.xlsx
│           ├── COOPAVEL 11012024__padrao_1__76098219000137__31122022__e5e5322d.xlsx
│           ├── Cooper Barras 29_09_2022__18c3925a.xlsx
│           ├── Cooper Barras 29_09_2022__padrao_1__40172765000123__31122021__18c3925a.xlsx
│           ├── COOPERALFA 27052026__0901b7a9.xlsx
│           ├── COOPERALFA 27052026__padrao_2__83305235000119__31122025__0901b7a9.xlsx
│           ├── COOPERALIANCA 11012024__613b9d5c.xlsx
│           ├── COOPERALIANCA 11012024__padrao_1__83647990000181__31122022__613b9d5c.xlsx
│           ├── COOPERALIANÇA 01102024__c8a99632.xlsx
│           ├── COOPERALIANÇA 01102024__padrao_1__83647990000181__31122023__c8a99632.xlsx
│           ├── Cooperativa AGRARIA 28032024__60bf71bf.xlsx
│           ├── Cooperativa AGRARIA 28032024__padrao_1__77890846000179__31122022__60bf71bf.xlsx
│           ├── COOPERATIVA REGIONAL AURIVERDE RATING 12__9305e149.xlsx
│           ├── COOPERATIVA REGIONAL AURIVERDE RATING 12__padrao_2__83731927000129__31122025__9305e149.xlsx
│           ├── COOPERLUZ 14082026__5be92039.xlsx
│           ├── COOPERLUZ 14082026__padrao_3__95824322000161__31122025__5be92039.xlsx
│           ├── COOPERVAL 14072026__7ad8dbf1.xlsx
│           ├── COOPERVAL 14072026__padrao_3__75084871000130__31122025__7ad8dbf1.xlsx
│           ├── COPACOL 18082023__fab51e04.xlsx
│           ├── COPACOL 18082023__padrao_1__76093731000190__31122022__fab51e04.xlsx
│           ├── COPACOL 19082026__4865a910.xlsx
│           ├── COPACOL 19082026__padrao_3__76093731000190__31122025__4865a910.xlsx
│           ├── COPACOL RATING 24102025__2b64b089.xlsx
│           ├── COPACOL RATING 24102025__padrao_2__76093731002649__2b64b089.xlsx
│           ├── COPACOL_25_08_2022 - 1__59299aa7.xlsx
│           ├── COPACOL_25_08_2022 - 1__padrao_1__76093731000190__31122021__59299aa7.xlsx
│           ├── COPACOL_25_08_2022 - 2__ec69b1dd.xlsx
│           ├── COPACOL_25_08_2022 - 2__padrao_1__76093731008256__31122021__ec69b1dd.xlsx
│           ├── COPAPA RATING 17112025__59db035a.xlsx
│           ├── COPAPA RATING 17112025__padrao_2__31590862000145__31122024__59db035a.xlsx
│           ├── COPAVEL RATING 11112025__4d442061.xlsx
│           ├── COPAVEL RATING 11112025__padrao_2__76098219000137__31122024__4d442061.xlsx
│           ├── COPREL 18082026__dafc322e.xlsx
│           ├── COPREL 18082026__padrao_3__90660754000160__31122025__dafc322e.xlsx
│           ├── Corteva 15_08_2022__7142529d.xlsx
│           ├── Corteva 15_08_2022__padrao_1__61064929000179__31122021__7142529d.xlsx
│           ├── Costa e Palu 16_08_2022__84b6e0cf.xlsx
│           ├── Costa e Palu 16_08_2022__padrao_1__07705880000140__31122021__84b6e0cf.xlsx
│           ├── CP KELKO RATING 02022026__d2d47311.xlsx
│           ├── CP KELKO RATING 02022026__padrao_2__54105671000146__31122025__d2d47311.xlsx
│           ├── CPIC 02_02_2023__01bb84dc.xlsx
│           ├── CPIC 02_02_2023__padrao_1__08670308000156__31122021__01bb84dc.xlsx
│           ├── CPTM 21072025__11a79b71.xlsx
│           ├── CPTM 21072025__padrao_1__71832679000123__31122024__11a79b71.xlsx
│           ├── CPTM 25062026__2b863724.xlsx
│           ├── CPTM 25062026__padrao_3__71832679000123__31122025__2b863724.xlsx
│           ├── CPTM RATING 19112025__c8a634fe.xlsx
│           ├── CRELUZ_09102024__6ea1af09.xlsx
│           ├── CRELUZ_09102024__padrao_1__91950261000128__31122023__6ea1af09.xlsx
│           ├── CRIUVA ENERGETICA 12062025__8b4c74df.xlsx
│           ├── CRIUVA ENERGETICA 12062025__padrao_1__07094315000194__31122024__8b4c74df.xlsx
│           ├── CSN 04062025__7c20df72.xlsx
│           ├── CSN 04062025__padrao_1__33042730000104__31122024__7c20df72.xlsx
│           ├── CSN 19062026__5ecc93e4.xlsx
│           ├── CSN 19062026__padrao_3__33042730000104__31122025__5ecc93e4.xlsx
│           ├── CSN 31-07-224__b329253d.xlsx
│           ├── CSN 31-07-224__padrao_1__33042730000104__31122023__b329253d.xlsx
│           ├── CSN CIMENTOS 08072025__d1a797bb.xlsx
│           ├── CSN CIMENTOS 08072025__padrao_1__60869336000117__31122024__d1a797bb.xlsx
│           ├── CSN CIMENTOS RATING 31102025__a4e06574.xlsx
│           ├── CSN MATRIZ RATING 06012026__cfdf5e3b.xlsx
│           ├── CSN MINERACAO 20072026__31a7704d.xlsx
│           ├── CSN MINERAÇÃO 22082025__d11c0b73.xlsx
│           ├── CSN MINERAÇÃO 22082025__padrao_1__08902291000115__31122024__d11c0b73.xlsx
│           ├── CSN MINERAÇÃO 22082025_consiste__b4536698.xlsx
│           ├── CSN MINERAÇÃO RATING 03112025__f2c64062.xlsx
│           ├── CVALE_09032023__9e31b9e6.xlsx
│           ├── CVALE_09032023__padrao_1__77863223000107__31122021__9e31b9e6.xlsx
│           ├── DAE SA AGUA E ESGOTO 18082023__87a745d7.xlsx
│           ├── DAE SA AGUA E ESGOTO 18082023__padrao_1__03582243000173__31122022__87a745d7.xlsx
│           ├── DANGLASS 29062026__a25a0b1b.xlsx
│           ├── DANGLASS 29062026__padrao_3__48992518000185__31122025__a25a0b1b.xlsx
│           ├── DAUS ALIMENTOS RATING 16032026__b8075dc5.xlsx
│           ├── DAUS ALIMENTOS RATING 16032026__padrao_2__04865228000103__31122025__b8075dc5.xlsx
│           ├── Delta Indústria Cerâmica 28022025__4cec4188.xlsx
│           ├── Delta Indústria Cerâmica 28022025__padrao_1__47595863000112__31122024__4cec4188.xlsx
│           ├── DEXCO - 15.07.2024__3b6dae11.xlsx
│           ├── DEXCO - 15.07.2024__padrao_1__97837181000147__31122023__3b6dae11.xlsx
│           ├── DEXCO 14072025__87e6f734.xlsx
│           ├── DEXCO 14072025__padrao_1__97837181000147__31122024__87e6f734.xlsx
│           ├── DEXCO 22062026__b8a32904.xlsx
│           ├── DEXCO 22062026__padrao_3__97837181000147__31122025__b8a32904.xlsx
│           ├── DEXCO RATING 19112025__a22ddd8d.xlsx
│           ├── DEXCO S.A._30-06-2022__60b32cbd.xlsx
│           ├── DEXCO S.A._30-06-2022__padrao_1__97837181000147__31122021__60b32cbd.xlsx
│           ├── DEXCO_28032023__4a186fc9.xlsx
│           ├── DEXCO_28032023__padrao_1__97837181000147__31122022__4a186fc9.xlsx
│           ├── Diagnósticos da América 08042025__e10dd7b7.xlsx
│           ├── Diagnósticos da América 08042025__padrao_1__61486650000183__31122024__e10dd7b7.xlsx
│           ├── DIP FRANGOS - 21072025__7d4d3396.xlsx
│           ├── DIP FRANGOS - 21072025__padrao_1__21819182000105__31122024__7d4d3396.xlsx
│           ├── DIP FRANGOS 28042026__81e7aa73.xlsx
│           ├── DIP FRANGOS 28042026__padrao_2__21819182000105__31122025__81e7aa73.xlsx
│           ├── DITIN 14072026__aac09cbc.xlsx
│           ├── Dois Marcos Sementes 03042024__019386a7.xlsx
│           ├── Dois Marcos Sementes 03042024__padrao_1__00291633000104__31122022__019386a7.xlsx
│           ├── DOW BRASIL RATING 21012026__cbd6f99f.xlsx
│           ├── Dulce Acqua_28_09_2022__386efd09.xlsx
│           ├── Dulce Acqua_28_09_2022__padrao_1__05126928000130__31122021__386efd09.xlsx
│           ├── DUPATRI HOSPITALAR__fae6571e.xlsx
│           ├── DUPATRI HOSPITALAR__padrao_2__04027894000164__31122025__fae6571e.xlsx
│           ├── DUPLAS RATING 09022026__e7b309fc.xlsx
│           ├── DUPLAS RATING 09022026__padrao_2__08740765000170__31122024__e7b309fc.xlsx
│           ├── EATON LTDA RATING 12032026__2e7ad42c.xlsx
│           ├── EATON_23_02_2022__49d808a2.xlsx
│           ├── EATON_23_02_2022__padrao_1__54625819000173__31122021__49d808a2.xlsx
│           ├── EBAZAR 18062026__ad67f37b.xlsx
│           ├── ECOURBIS - 17062026__6de8ad5c.xlsx
│           ├── ECOURBIS - 17062026__padrao_3__07037123000146__31122025__6de8ad5c.xlsx
│           ├── EDF 24072025 v2__94afbcc1.xlsx
│           ├── EDF 24072025 v2__padrao_1__21812954000179__31122024__94afbcc1.xlsx
│           ├── EDF 24072025__28183b18.xlsx
│           ├── EDF RATING 24122025__578fbef5.xlsx
│           ├── EDF VERDECOM RATING 17102025__de332121.xlsx
│           ├── EDF VERDECOM RATING 17102025__padrao_2__35984409000174__31122024__de332121.xlsx
│           ├── ELEKEIROZ 15052024__d921eda6.xlsx
│           ├── ELEKEIROZ 15052024__padrao_1__76093731000190__31122023__d921eda6.xlsx
│           ├── ELEKEIROZ 19082026__c86acae8.xlsx
│           ├── ELEKEIROZ 19082026__padrao_3__13788120000147__31122025__c86acae8.xlsx
│           ├── ELEKEIROZ_15_08_2024__619c79c6.xlsx
│           ├── ELEKEIROZ_15_08_2024__padrao_1__13788120000147__31122023__619c79c6.xlsx
│           ├── Eletrobras_30052025__8cd5a9f3.xlsx
│           ├── Eletrobras_30052025__padrao_1__00001180000126__31122024__8cd5a9f3.xlsx
│           ├── ELFA MEDICAMENTOS 22052026__a81dcd22.xlsx
│           ├── ELFA MEDICAMENTOS 22052026__padrao_2__09053134000145__31122025__a81dcd22.xlsx
│           ├── Elizabeth Porcelanato__efb2f4c5.xlsx
│           ├── Elizabeth Porcelanato__padrao_1__02357659000125__31122021__efb2f4c5.xlsx
│           ├── EMBASA 14042025__f3945173.xlsx
│           ├── EMBASA 14042025__padrao_1__13504675000110__31122024__f3945173.xlsx
│           ├── EMBASA 18062026__584292c0.xlsx
│           ├── EMBASA 18062026__padrao_3__13504675000110__31122025__584292c0.xlsx
│           ├── EMBASA RATING 01122025__63a52d01.xlsx
│           ├── EMBRAER 05052026__ce58c10e.xlsx
│           ├── EMBRAER 05052026__padrao_2__07689002000189__31122025__ce58c10e.xlsx
│           ├── EMBRAER_10042023__60c03ecf.xlsx
│           ├── EMBRAER_10042023__padrao_1__07689002000189__31122022__60c03ecf.xlsx
│           ├── ENERPEIXE 15092025__fb5ffb44.xlsx
│           ├── ENERPEIXE 15092025__padrao_1__04426411000102__31122024__fb5ffb44.xlsx
│           ├── Engetech 10032025__11be1112.xlsx
│           ├── Engetech 10032025__padrao_1__01144673000188__31122024__11be1112.xlsx
│           ├── EPASA 21122023__f5ebed0d.xlsx
│           ├── EPASA 21122023__padrao_1__10366780000141__31122022__f5ebed0d.xlsx
│           ├── ESTADO DE SP 15_08_2022__b5284966.xlsx
│           ├── ESTADO DE SP 15_08_2022__padrao_1__61533949000141__31122021__b5284966.xlsx
│           ├── ETERNIT RATING 18122025__5f5b7005.xlsx
│           ├── ETERNIT RATING 18122025__padrao_2__61092037000181__31122024__5f5b7005.xlsx
│           ├── EUCATEX RATING 28102025__01b2486d.xlsx
│           ├── EUCATEX RATING 28102025__padrao_2__14675270000107__31122024__01b2486d.xlsx
│           ├── EUROFARMA_03102023__80fe120d.xlsx
│           ├── EUROFARMA_03102023__padrao_1__61190096002136__31122022__80fe120d.xlsx
│           ├── EVONIK 04112024__92ca6f26.xlsx
│           ├── EVONIK 04112024__padrao_1__62695036000194__31122023__92ca6f26.xlsx
│           ├── EVONIK 13082025__1dec7ef6.xlsx
│           ├── EVONIK 13082025__padrao_1__62695036000194__31122024__1dec7ef6.xlsx
│           ├── EVONIK 29052026__3d99e03b.xlsx
│           ├── EVONIK 29052026__padrao_2__62695036000194__31122025__3d99e03b.xlsx
│           ├── EVONIK RATING 19112025__b3d41047.xlsx
│           ├── EVONIK_16062023__0133c528.xlsx
│           ├── EVONIK_16062023__padrao_1__62695036000194__31122022__0133c528.xlsx
│           ├── EVONIK_FILIAL 04112024__c19ec17f.xlsx
│           ├── EVONIK_FILIAL 04112024__padrao_1__62695036005404__31122023__c19ec17f.xlsx
│           ├── EXTRAMIX - Avaliação Middle__04d329eb.xlsx
│           ├── EXTRAMIX - Avaliação Middle__padrao_1__11517262000144__31122021__04d329eb.xlsx
│           ├── EXTRUSAICK 17062026__53315ac2.xlsx
│           ├── EXTRUSAICK 17062026__padrao_3__40772936000155__31122025__53315ac2.xlsx
│           ├── FACCHINI SA 22122025__eee64e6a.xlsx
│           ├── FACCHINI SA 22122025__padrao_2__03509978000171__31122024__eee64e6a.xlsx
│           ├── FACCHINI_20022025__1eb8d855.xlsx
│           ├── FACCHINI_20022025__padrao_1__03509978000171__31122023__1eb8d855.xlsx
│           ├── FACULDADES ALFA RATING 29102025__29e60c20.xlsx
│           ├── FACULDADES ALFA RATING 29102025__padrao_2__02850990000182__31122024__29e60c20.xlsx
│           ├── FCA Fiat-Chrysler_22_08_2022__2a28dad2.xlsx
│           ├── FCA Fiat-Chrysler_22_08_2022__padrao_1__16701716003686__31122021__2a28dad2.xlsx
│           ├── FERBASA 00355224__c5b05af3.xlsx
│           ├── FERBASA 00355224__padrao_1__15141799000103__31122024__c5b05af3.xlsx
│           ├── FERBASA 28052026__0fb308d6.xlsx
│           ├── FERBASA 28052026__padrao_2__15141799000103__31122025__0fb308d6.xlsx
│           ├── FERBASA RATING 03122025__665533f5.xlsx
│           ├── FERNANDEZ INDUSTRIA DE PAPEL RATING 0903__1425d01b.xlsx
│           ├── FERNANDEZ INDUSTRIA DE PAPEL RATING 0903__padrao_2__43468701000162__31122024__1425d01b.xlsx
│           ├── FGV 15102025__c39b622a.xlsx
│           ├── FGV 15102025__padrao_2__33641663000144__c39b622a.xlsx
│           ├── Fiação São Bento 08_11_2022__f350f198.xlsx
│           ├── Fiação São Bento 08_11_2022__padrao_1__86046414000177__31122021__f350f198.xlsx
│           ├── FIBRAPLAC 22102025__1da1ed9e.xlsx
│           ├── FIBRAPLAC_12_08_2024__10dc7351.xlsx
│           ├── FIBRAPLAC_12_08_2024__padrao_1__04176791000247__31122023__10dc7351.xlsx
│           ├── ficha ARAUCO 2022__42324b70.xlsx
│           ├── ficha ARAUCO 2022__padrao_1__76518836000144__31122020__42324b70.xlsx
│           ├── ficha BASF 2022__2be29b10.xlsx
│           ├── ficha BASF 2022__padrao_1__48539407007392__31122021__2be29b10.xlsx
│           ├── FICHA CONSUMIDORES V1 (2)_VALE_PREENCHID__96ea0158.xlsx
│           ├── FICHA CONSUMIDORES V1 (2)_VALE_PREENCHID__padrao_3__33592510000154__31122025__96ea0158.xlsx
│           ├── ficha FERBASA 2022__f07a2e54.xlsx
│           ├── ficha FERBASA 2022__padrao_1__15141799000103__31122021__f07a2e54.xlsx
│           ├── FICHA MODELO ddmmaaaa__e143673a.xlsx
│           ├── FICHA MODELO ddmmaaaa__padrao_1__06164824000183__31122023__e143673a.xlsx
│           ├── ficha modelo livres acima de 2MWm__7afaa4a4.xlsx
│           ├── ficha modelo livres acima de 2MWm__padrao_1__33200056000149__31122022__7afaa4a4.xlsx
│           ├── FICHA MODELO NOVA DDMMAA__6e0b3677.xlsx
│           ├── ficha SANTHER 2022-10__52885eed.xlsx
│           ├── ficha SANTHER 2022-10__padrao_1__61101895003918__31122021__52885eed.xlsx
│           ├── ficha São Eutiquiano Participações (Grup__bbcc8781.xlsx
│           ├── ficha São Eutiquiano Participações (Grup__padrao_1__12125536000112__31122021__bbcc8781.xlsx
│           ├── ficha Yara Brasil Fertilizantes SA 2022__466d79b7.xlsx
│           ├── ficha Yara Brasil Fertilizantes SA 2022__padrao_1__92660604000182__31122021__466d79b7.xlsx
│           ├── FICHA_CONSUMIDORES_AMSTED_MAXXION_PREENC__bb93f28f.xlsx
│           ├── FICHA_CONSUMIDORES_AMSTED_MAXXION_PREENC__padrao_3__01599436000101__31082025__bb93f28f.xlsx
│           ├── FICHA_CONSUMIDORES_CORSAN_PREENCHIDA__c1382859.xlsx
│           ├── FICHA_CONSUMIDORES_CORSAN_PREENCHIDA__padrao_3__92802784000190__31122025__c1382859.xlsx
│           ├── FICHA_CONSUMIDORES_FS_BIOENERGIA_CORRIGI__38e5ddcc.xlsx
│           ├── FICHA_CONSUMIDORES_FS_BIOENERGIA_CORRIGI__padrao_3__20003699000150__31032026__38e5ddcc.xlsx
│           ├── FICHA_CONSUMIDORES_GV_DO_BRASIL_FINAL__7ad7c88c.xlsx
│           ├── FICHA_CONSUMIDORES_GV_DO_BRASIL_FINAL__padrao_3__12884632000144__31122025__7ad7c88c.xlsx
│           ├── FICHA_CONSUMIDORES_MILI_SA_PREENCHIDA__e554d79b.xlsx
│           ├── FICHA_CONSUMIDORES_MILI_SA_PREENCHIDA__padrao_3__78908266000124__31122025__e554d79b.xlsx
│           ├── FICHA_CONSUMIDORES_UNIMED_SOROCABA_PREEN__8f3f21dd.xlsx
│           ├── FICHA_CONSUMIDORES_UNIMED_SOROCABA_PREEN__padrao_3__45399961000159__31122025__8f3f21dd.xlsx
│           ├── FICHA_CONSUMIDORES_V1_CEESAM_PREENCHIDA __2485a794.xlsx
│           ├── FICHA_CONSUMIDORES_V1_CEESAM_PREENCHIDA __padrao_3__85937316000167__31122025__2485a794.xlsx
│           ├── Fontain 05032024__f330b158.xlsx
│           ├── Fontain 05032024__padrao_1__10622118000105__31122022__f330b158.xlsx
│           ├── FOSNOR 20-02-225__5f83b303.xlsx
│           ├── FOSNOR 20-02-225__padrao_1__32112142000137__31122023__5f83b303.xlsx
│           ├── Frigoestrela_02052023__73fa1a2d.xlsx
│           ├── Frigoestrela_02052023__padrao_1__52645009000153__31122022__73fa1a2d.xlsx
│           ├── FRIGOESTRELA_20_08_2024__3f9a298b.xlsx
│           ├── FRIGOESTRELA_20_08_2024__padrao_1__52645009000153__31122023__3f9a298b.xlsx
│           ├── FRIMESA - 08 04 2024__f0d68a94.xlsx
│           ├── FRIMESA - 08 04 2024__padrao_1__77595395000147__31122023__f0d68a94.xlsx
│           ├── FRISIA_03102023__1c5519c3.xlsx
│           ├── FRISIA_03102023__padrao_1__76107770000108__31122022__1c5519c3.xlsx
│           ├── GAB 10012024__0e035133.xlsx
│           ├── GAB 10012024__padrao_1__09266129000110__31122022__0e035133.xlsx
│           ├── GAZIT 05022024__afceaebd.xlsx
│           ├── GAZIT 05022024__padrao_1__08903942000191__afceaebd.xlsx
│           ├── GERDAU ACOMINAS RATING 11122025__c33ad803.xlsx
│           ├── GERDAU ACOMINAS RATING 11122025__padrao_2__17227422000105__31122024__c33ad803.xlsx
│           ├── GERDAU ACOS LONGOS - 00482085__c8604bb3.xlsx
│           ├── GERDAU ACOS LONGOS - 00482085__padrao_2__07358761005632__31122025__c8604bb3.xlsx
│           ├── GERDAU Açominas 11122024__27d74962.xlsx
│           ├── GERDAU Açominas 11122024__padrao_1__17227422000105__31122023__27d74962.xlsx
│           ├── GERDAU AÇOMINAS 13062025__4cc3b059.xlsx
│           ├── GERDAU Aços Longos 11122024__db3be5db.xlsx
│           ├── GERDAU Aços Longos 11122024__padrao_1__07358761000169__31122023__db3be5db.xlsx
│           ├── GERDAU AÇOS LONGOS 13062025__f9069969.xlsx
│           ├── GERDAU AÇOS LONGOS 13062025__padrao_1__07358761000169__31122024__f9069969.xlsx
│           ├── GERDAU AÇOS LONGOS RATING 15102025__e381b84b.xlsx
│           ├── GERDAU AÇOS LONGOS RATING 15102025__padrao_2__07358761000169__e381b84b.xlsx
│           ├── GERDAU AÇOS LONGOS RATING 27032026__903f777c.xlsx
│           ├── GERDAU MATRIZ 20052026__d7894696.xlsx
│           ├── GERDAU MATRIZ 20052026__padrao_2__33611500000119__31122025__d7894696.xlsx
│           ├── GERDAU SA - 13062025__ff49d357.xlsx
│           ├── GERDAU SA - 13062025__padrao_1__33611500000119__31122024__ff49d357.xlsx
│           ├── GERDAU SA 11122024__ba5db8b0.xlsx
│           ├── GERDAU SA 11122024__padrao_1__33611500000119__31122023__ba5db8b0.xlsx
│           ├── GERDAU SA RATING 12122025__d42aa1e1.xlsx
│           ├── GERDAU_23062023__826f2f98.xlsx
│           ├── GERDAU_23062023__padrao_1__33611500000119__31122022__826f2f98.xlsx
│           ├── Globalpack 17012024__47406b36.xlsx
│           ├── Globalpack 17012024__padrao_1__04558449000392__31122022__47406b36.xlsx
│           ├── GM do Brasil - Avaliação Middle__1db2ba16.xlsx
│           ├── GM do Brasil - Avaliação Middle__padrao_1__59275792000150__31122022__1db2ba16.xlsx
│           ├── GM RATING 16012026__0d186827.xlsx
│           ├── Goodyear 2022-07-12__0c561fbb.xlsx
│           ├── Goodyear 2022-07-12__padrao_1__60500246000154__31122021__0c561fbb.xlsx
│           ├── GPA RATING 07112025__346a9c32.xlsx
│           ├── GPA RATING 07112025__padrao_2__47508411000156__31122024__346a9c32.xlsx
│           ├── Grendene 2022-07-28__77d7af6b.xlsx
│           ├── Grendene 2022-07-28__padrao_1__89850341000160__31122021__77d7af6b.xlsx
│           ├── Grupo Barigui 05_09_2022__54250ddf.xlsx
│           ├── Grupo Barigui 05_09_2022__padrao_1__79763884000196__31122021__54250ddf.xlsx
│           ├── Grupo GAZIT 10012024__b4773a4e.xlsx
│           ├── Grupo GAZIT 10012024__padrao_1__08903942000191__31122022__b4773a4e.xlsx
│           ├── GRUPO LIDER RATING 11122025__de54ce01.xlsx
│           ├── GRUPO LIDER RATING 11122025__padrao_2__05054671000159__31122024__de54ce01.xlsx
│           ├── GRUPO MATHEUS RATING 10032026__ffa5400f.xlsx
│           ├── GRUPO MATHEUS RATING 10032026__padrao_2__24990777000109__31122024__ffa5400f.xlsx
│           ├── Grupo NC - Avaliação Middle__9216b56b.xlsx
│           ├── Grupo NC - Avaliação Middle__padrao_1__57507378000365__31122021__9216b56b.xlsx
│           ├── Grupo Pão de Açucar 19032024__3bc33db2.xlsx
│           ├── Grupo Pão de Açucar 19032024__padrao_1__47508411000156__31122023__3bc33db2.xlsx
│           ├── Grupo Rocha 23082023__ae38bc26.xlsx
│           ├── Grupo Rocha 23082023__padrao_1__13200257000139__31122022__ae38bc26.xlsx
│           ├── Grupo São Camilo 16_09_2022__1f25a956.xlsx
│           ├── Grupo São Camilo 16_09_2022__padrao_1__60975737000151__31122021__1f25a956.xlsx
│           ├── Grupo Vertical 30082023__00057821.xlsx
│           ├── Grupo Vertical 30082023__padrao_1__37589182000198__31122022__00057821.xlsx
│           ├── GTFOODS 00354264__81e96500.xlsx
│           ├── GTFOODS 00354264__padrao_1__85070068000108__31122024__81e96500.xlsx
│           ├── GTFOODS 15072026__9cdf4f86.xlsx
│           ├── GTFOODS 15072026__padrao_3__85070068000108__31122025__9cdf4f86.xlsx
│           ├── GTFOODS RATING 26052026__deb67ffb.xlsx
│           ├── GTOP RATING 12122025__d93eeb92.xlsx
│           ├── GTOP RATING 12122025__padrao_2__18803654000461__31122024__d93eeb92.xlsx
│           ├── GUERRO 08042024__d29904a0.xlsx
│           ├── GUERRO 08042024__padrao_1__09461639000149__31122022__d29904a0.xlsx
│           ├── GWEST RATING 03022026__eeb136a9.xlsx
│           ├── GWEST RATING 03022026__padrao_2__34954956000144__31122024__eeb136a9.xlsx
│           ├── HAVAN - 08082025__6ab8b107.xlsx
│           ├── HAVAN - 08082025__padrao_1__79379491000183__31122024__6ab8b107.xlsx
│           ├── HAVAN RATING 03112025__e68aee07.xlsx
│           ├── HAVAN SA 06042026__523419f3.xlsx
│           ├── HAVAN SA 06042026__padrao_2__79379491000183__31122025__523419f3.xlsx
│           ├── Heinz Brasil - Avaliação Middle__e4804c2d.xlsx
│           ├── Heinz Brasil - Avaliação Middle__padrao_1__50955707000120__31122021__e4804c2d.xlsx
│           ├── HEINZ_20032023__a73afcbb.xlsx
│           ├── HEINZ_20032023__padrao_1__50955707001100__31122021__a73afcbb.xlsx
│           ├── HEJSN_19_10_2022__52185f15.xlsx
│           ├── HEJSN_19_10_2022__padrao_1__28127926000242__31122021__52185f15.xlsx
│           ├── HF SISTEMAS DE FREIOS RATING 26012026__a8228e5a.xlsx
│           ├── HF SISTEMAS DE FREIOS RATING 26012026__padrao_2__09075317000161__31122024__a8228e5a.xlsx
│           ├── Hospital Cruz Vermelha - Avaliação Middl__329e42d8.xlsx
│           ├── Hospital Cruz Vermelha - Avaliação Middl__padrao_1__07404052000172__31122021__329e42d8.xlsx
│           ├── HOSPITAL EVANLEGICO DE LONDRINA 20072026__af0f784d.xlsx
│           ├── HOSPITAL EVANLEGICO DE LONDRINA 20072026__padrao_3__78613841000161__31122025__af0f784d.xlsx
│           ├── Hospital Jaraguá 25072023__081ce2bd.xlsx
│           ├── Hospital Jaraguá 25072023__padrao_1__39913479000192__31122022__081ce2bd.xlsx
│           ├── Hospital Moinhos de Vento 22_09_2022__307aba69.xlsx
│           ├── Hospital Moinhos de Vento 22_09_2022__padrao_1__92685833000151__31122021__307aba69.xlsx
│           ├── Hospital Pequeno Principe 29_09_2022__97825977.xlsx
│           ├── Hospital Pequeno Principe 29_09_2022__padrao_1__76591569000130__31122021__97825977.xlsx
│           ├── Hospital Policlina Cascavel 2023-01-26__58119da9.xlsx
│           ├── Hospital Policlina Cascavel 2023-01-26__padrao_1__76081892000164__31122021__58119da9.xlsx
│           ├── Hospital São Francisco18_01_23__e49cdaef.xlsx
│           ├── Hospital São Francisco18_01_23__padrao_1__54672449000125__31122021__e49cdaef.xlsx
│           ├── HOSPITAL_NOSSA_SENHORA_DAS_DORES_2103202__38c5670b.xlsx
│           ├── HOSPITAL_NOSSA_SENHORA_DAS_DORES_2103202__padrao_1__23798846000114__31122021__38c5670b.xlsx
│           ├── HUBNER 19022024__43f424fd.xlsx
│           ├── HUBNER 19022024__padrao_1__06886749000407__31122022__43f424fd.xlsx
│           ├── Hyundai_10082023__37d1409f.xlsx
│           ├── Hyundai_10082023__padrao_1__10394422000142__31122022__37d1409f.xlsx
│           ├── Incepa 20052024__1aab925d.xlsx
│           ├── Incepa 20052024__padrao_1__76610062000187__1aab925d.xlsx
│           ├── INDEMIL 27112024__b893dc0d.xlsx
│           ├── INDEMIL 27112024__padrao_1__61887899000109__31122023__b893dc0d.xlsx
│           ├── INDEMIL RATING 23032026 - Copia__10310b50.xlsx
│           ├── INDEMIL RATING 23032026 - Copia__padrao_2__61887899000109__31122025__10310b50.xlsx
│           ├── INDEMIL RATING 23032026__95680e2d.xlsx
│           ├── INDUPA 14072025__bcf440d3.xlsx
│           ├── INDUPA 19052026__ffa626f3.xlsx
│           ├── INDUPA 19052026__padrao_2__61460325000141__31122025__ffa626f3.xlsx
│           ├── INDUPA RATING 03112025__8f0380b7.xlsx
│           ├── INDUPA RATING 03112025__padrao_2__61460325000141__31122024__8f0380b7.xlsx
│           ├── INDUSTRIA VIDREIRA DO NORDESTE RATING 04__e2280bbb.xlsx
│           ├── INDUSTRIA VIDREIRA DO NORDESTE RATING 04__padrao_2__16433626000121__12072012__e2280bbb.xlsx
│           ├── INPASA RATING 10122025__a709f844.xlsx
│           ├── INPASA RATING 10122025__padrao_2__29316596000115__31122024__a709f844.xlsx
│           ├── Intercast - Avaliação Middle__02d75fb7.xlsx
│           ├── Intercast - Avaliação Middle__padrao_1__02326750000183__31122021__02d75fb7.xlsx
│           ├── INTERCEMENT - 08072025__245958a9.xlsx
│           ├── INTERCEMENT - 08072025__padrao_1__62258884000136__31122024__245958a9.xlsx
│           ├── INTERCEMENT RATING 13102025__fc328776.xlsx
│           ├── INTERCEMENT RATING 13102025__padrao_2__62258884000136__fc328776.xlsx
│           ├── INTERCEMENT RATING 19032026__35e8eca2.xlsx
│           ├── INTERCEMENT RATING 19032026__padrao_2__62258884000136__31122025__35e8eca2.xlsx
│           ├── InterCement_20_10_2022__72cfc0b3.xlsx
│           ├── InterCement_20_10_2022__padrao_1__62258884000136__31122021__72cfc0b3.xlsx
│           ├── IPIRANGA AGROINDUSTRIAL 0605026__8327a90c.xlsx
│           ├── IPIRANGA AGROINDUSTRIAL 0605026__padrao_2__07280328001804__31032025__8327a90c.xlsx
│           ├── IRANI_07-07-2022__d0bf138c.xlsx
│           ├── IRANI_07-07-2022__padrao_1__92791243000103__31122021__d0bf138c.xlsx
│           ├── IRGOVEL 28072026__31a7704d.xlsx
│           ├── Itambe 03042024__685e7c5e.xlsx
│           ├── Itambe 03042024__padrao_1__76630573000160__31122023__685e7c5e.xlsx
│           ├── ITAMBE CIMENTOS 24072026__752f27cc.xlsx
│           ├── ITAMBE CIMENTOS 24072026__padrao_3__76630573000160__31122025__752f27cc.xlsx
│           ├── ITAMBE ENERGETICA SA 18082025__f03e61f1.xlsx
│           ├── ITAMBE ENERGETICA SA 18082025__padrao_1__76630573000160__31122024__f03e61f1.xlsx
│           ├── ITAMBE MATRIZ - 17092025__ebd252a5.xlsx
│           ├── ITAMBE MATRIZ RATING 16102025__1fe4dd3c.xlsx
│           ├── Jacobina Mineração_24_02_2023__327ee7b7.xlsx
│           ├── Jacobina Mineração_24_02_2023__padrao_1__42463174000130__31122021__327ee7b7.xlsx
│           ├── JAGUAFRANGOS 08012024__fe546df1.xlsx
│           ├── JAGUAFRANGOS 08012024__padrao_1__85090033000122__31122022__fe546df1.xlsx
│           ├── Jardim Botânico Participações 28-10-2025__b2180e91.xlsx
│           ├── Jardim Botânico Participações 28-10-2025__padrao_2__24550050000100__31122024__b2180e91.xlsx
│           ├── JBS 11012024__d0764404.xlsx
│           ├── JBS 11012024__padrao_1__02916265000160__31122022__d0764404.xlsx
│           ├── JBS 13052026__99adab02.xlsx
│           ├── JBS 13052026__padrao_2__02916265000160__31122025__99adab02.xlsx
│           ├── JBS SA - 08072025__076745bf.xlsx
│           ├── JBS SA - 08072025__padrao_1__02916265000160__31122024__076745bf.xlsx
│           ├── JBS SA RATING 06112025__d46d991b.xlsx
│           ├── JBSFILIAL_01102024__7fdf951b.xlsx
│           ├── JBSFILIAL_01102024__padrao_1__02916265037322__31122023__7fdf951b.xlsx
│           ├── KARSTEN - 15.07.2024__60926115.xlsx
│           ├── KARSTEN - 15.07.2024__padrao_1__82640558000104__31122023__60926115.xlsx
│           ├── Karsten 12_09_2022__c27c6ec1.xlsx
│           ├── Karsten 12_09_2022__padrao_1__82640558000104__31122021__c27c6ec1.xlsx
│           ├── KARSTEN SA 09102025__b0eb3c66.xlsx
│           ├── KARSTEN SA 09102025__padrao_2__82640558000104__b0eb3c66.xlsx
│           ├── Kimberly-Clark análises__8efa8360.xlsx
│           ├── Kimberly-Clark análises__padrao_1__02290277000121__31122021__8efa8360.xlsx
│           ├── KINROSS 28102025__f9e1ec67.xlsx
│           ├── KINROSS 28102025__padrao_2__20346524000146__31122025__f9e1ec67.xlsx
│           ├── Klabin 03112023__ecc4e69a.xlsx
│           ├── Klabin 03112023__padrao_2__89637490000145__ecc4e69a.xlsx
│           ├── Klabin 12062024__38f77c59.xlsx
│           ├── Klabin 12062024__padrao_1__89637490000145__31122023__38f77c59.xlsx
│           ├── KLABIN 15052026__336078de.xlsx
│           ├── KLABIN 15052026__padrao_2__89637490000145__31122025__336078de.xlsx
│           ├── KLABIN 18_02_2022__43b7c8fe.xlsx
│           ├── KLABIN 18_02_2022__padrao_1__89637490000145__31122021__43b7c8fe.xlsx
│           ├── Klabin 26032025__95b78736.xlsx
│           ├── Klabin 26032025__padrao_1__89637490000145__31122024__95b78736.xlsx
│           ├── Klabin Rating 17102025__790813fa.xlsx
│           ├── KORDSA_13032025__f5ca9860.xlsx
│           ├── KORDSA_13032025__padrao_1__13573332000107__31122023__f5ca9860.xlsx
│           ├── KORDSA_20_04_2022__fb64e12b.xlsx
│           ├── KORDSA_20_04_2022__padrao_1__13573332000107__31122021__fb64e12b.xlsx
│           ├── KRONA TUBOS e CONEXOES 28042025__3c5b11ac.xlsx
│           ├── KRONA TUBOS e CONEXOES 28042025__padrao_1__11907140000164__31122024__3c5b11ac.xlsx
│           ├── LAR COOPERATIVA 03072025__af80c124.xlsx
│           ├── LAR COOPERATIVA 03072025__padrao_1__77752293000198__31122024__af80c124.xlsx
│           ├── LAR COOPERATIVA 07012024 v2__05b53361.xlsx
│           ├── LAR COOPERATIVA 07012024 v2__padrao_1__77752293000198__31122023__05b53361.xlsx
│           ├── LAR COOPERATIVA RATING 18112025__fefd7dc1.xlsx
│           ├── Laticínios Ruhban 09102025__125bd4ef.xlsx
│           ├── Laticínios Ruhban 09102025__padrao_2__00529188000160__125bd4ef.xlsx
│           ├── LAVANDERIA JUSSARA 05052026__e5ab6a94.xlsx
│           ├── LDC 09102025 RATING__7a3537c9.xlsx
│           ├── LDC 09102025 RATING__padrao_2__47067525000108__7a3537c9.xlsx
│           ├── LDC BRASIL 30062025__8859b20a.xlsx
│           ├── LDC BRASIL 30062025__padrao_1__47067525000108__31122024__8859b20a.xlsx
│           ├── LDC MATRIZ__f5a61bac.xlsx
│           ├── LDC MATRIZ__padrao_2__47067525000108__31122025__f5a61bac.xlsx
│           ├── LDC SUCOS 06052026__3abde46b.xlsx
│           ├── LDC SUCOS 06052026__padrao_2__00831373000104__31122025__3abde46b.xlsx
│           ├── LDC SUCOS 30062025__4033bbcd.xlsx
│           ├── LDC SUCOS 30062025__padrao_1__00831373000104__31122024__4033bbcd.xlsx
│           ├── LDC SUCOS RATING 13112025__8d2a654d.xlsx
│           ├── LDC TES 10102025 RATING__fd5967b0.xlsx
│           ├── LDC TES 10102025 RATING__padrao_2__18845076000183__fd5967b0.xlsx
│           ├── LDC TES 30062025__9caa9b20.xlsx
│           ├── LDC TES 30062025__padrao_1__18845076000183__31122024__9caa9b20.xlsx
│           ├── LIASA 05012024 v2__fd466e74.xlsx
│           ├── LIASA 05012024 v2__padrao_1__17221771000101__31122022__fd466e74.xlsx
│           ├── LIASA 18062025__81507629.xlsx
│           ├── LIASA 18062025__padrao_1__17221771000101__31122024__81507629.xlsx
│           ├── LIASA RATING 24102025__00ddca54.xlsx
│           ├── LIASA RATING 24102025__padrao_2__17221771000101__31122023__00ddca54.xlsx
│           ├── LIASA RATING 29102025__bbfbf70f.xlsx
│           ├── LIBRA LIGAS - 08 04 2024__2c592270.xlsx
│           ├── LIBRA LIGAS - 08 04 2024__padrao_1__10500221000182__31122022__2c592270.xlsx
│           ├── LIBRAS RATING 09032026__c30c7fde.xlsx
│           ├── LIBRAS RATING 09032026__padrao_2__10500221000182__31122024__c30c7fde.xlsx
│           ├── LIGA ALVARO BAHIA RATING 03112025__081ce4f0.xlsx
│           ├── LIGA ALVARO BAHIA RATING 03112025__padrao_2__15170723000106__31122024__081ce4f0.xlsx
│           ├── LINHA 4 - MOTIVA 06072026__777060f0.xlsx
│           ├── LINHA 4 - MOTIVA 06072026__padrao_3__07682638000107__31122025__777060f0.xlsx
│           ├── LINHAS 5 E 17 06072026__5c426bda.xlsx
│           ├── LINHAS 5 E 17 06072026__padrao_3__29938085000135__31122025__5c426bda.xlsx
│           ├── LINHAS 8 E 9 07072026__75010051.xlsx
│           ├── LINHAS 8 E 9 07072026__padrao_3__42288184000187__31122025__75010051.xlsx
│           ├── LSNC RATING 12122025__94615dd1.xlsx
│           ├── LSNC RATING 12122025__padrao_2__55924836000174__31122024__94615dd1.xlsx
│           ├── LUME CERAMICA 14042026__b5cc3f5f.xlsx
│           ├── LUME CERAMICA 14042026__padrao_2__04201168000116__31122024__b5cc3f5f.xlsx
│           ├── LYCRA_22062023__8c3a4c60.xlsx
│           ├── LYCRA_22062023__padrao_1__00021096000417__31122021__8c3a4c60.xlsx
│           ├── LÍDER (Atacadista) 02122024__70b723d0.xlsx
│           ├── LÍDER (Atacadista) 02122024__padrao_1__05054671000159__31122023__70b723d0.xlsx
│           ├── M DIAS BRANCO 08062026__aa03fa61.xlsx
│           ├── M DIAS BRANCO 08062026__padrao_3__07206816000115__31122025__aa03fa61.xlsx
│           ├── M DIAS BRANCO 15082025__2908e2ca.xlsx
│           ├── M DIAS BRANCO 15082025__padrao_1__07206816000115__31122024__2908e2ca.xlsx
│           ├── M DIAS BRANCO 15082025_consiste__aead5817.xlsx
│           ├── M DIAS BRANCO RATING 03112025__4e657c39.xlsx
│           ├── MAHLE 13082026__69d35748.xlsx
│           ├── MAHLE 13082026__padrao_3__60476884000187__31122025__69d35748.xlsx
│           ├── MARFRIG RATING 05112025__65733912.xlsx
│           ├── MARFRIG RATING 05112025__padrao_2__03853896000140__31122024__65733912.xlsx
│           ├── MARINGA FERRO LIGA 18062026__063a5587.xlsx
│           ├── MARINGA FERRO LIGA 18062026__padrao_3__61082988000170__31122025__063a5587.xlsx
│           ├── MARINGA FERRO LIGA 26082025__f481945d.xlsx
│           ├── MARINGA FERRO LIGA 26082025__padrao_1__61082988000170__31122024__f481945d.xlsx
│           ├── MARINGA FERRO LIGA RATING 31102025__9b9dd3a6.xlsx
│           ├── MBRF_09062026__a261f1c9.xlsx
│           ├── MBRF_09062026__padrao_3__03853896000140__31122025__a261f1c9.xlsx
│           ├── MESSER GASES 02072025__4a1a3122.xlsx
│           ├── MESSER GASES 02072025__padrao_1__60619202000148__31122024__4a1a3122.xlsx
│           ├── Messer Gases 16112023__24a9ae63.xlsx
│           ├── Messer Gases 16112023__padrao_1__60619202000148__31122022__24a9ae63.xlsx
│           ├── MESSER GASES 22072026__171dc857.xlsx
│           ├── MESSER GASES 22072026__padrao_3__60619202000148__31122025__171dc857.xlsx
│           ├── MESSER GASES_05052022__9fe720c6.xlsx
│           ├── MESSER GASES_05052022__padrao_1__60619202003325__31122021__9fe720c6.xlsx
│           ├── MESSER_27_12_2022__d587eeb1.xlsx
│           ├── MESSER_27_12_2022__padrao_1__60619202000148__31122021__d587eeb1.xlsx
│           ├── MESSES GASES RATING 12112025__6cde5405.xlsx
│           ├── METAL LEVE - 21082025__4e81cb8e.xlsx
│           ├── METAL LEVE - 21082025__padrao_1__60476884000187__31122024__4e81cb8e.xlsx
│           ├── METAL LEVE RATING 18022026__216d5349.xlsx
│           ├── METAL LEVE RATING 31102025__9df58e21.xlsx
│           ├── METALBRAZING 11062026__545f8f43.xlsx
│           ├── METALBRAZING 11062026__padrao_3__05251919000171__31122025__545f8f43.xlsx
│           ├── METRO 15072025__08cd6789.xlsx
│           ├── METRO 15072025__padrao_1__62070362000106__31122024__08cd6789.xlsx
│           ├── METRO BAHIA 08102025__ba58f9cb.xlsx
│           ├── METRO BAHIA 08102025__padrao_2__18891185000137__ba58f9cb.xlsx
│           ├── Metro Bahia 18042024__614256c5.xlsx
│           ├── Metro Bahia 18042024__padrao_1__02846056000197__31122023__614256c5.xlsx
│           ├── METRO BAHIA 21082025__59440162.xlsx
│           ├── METRO BAHIA 21082025__padrao_1__18891185000137__31122024__59440162.xlsx
│           ├── METRO BAHIA RATING 19112025__70eb65ae.xlsx
│           ├── METRO RATING 26112025__2f37554b.xlsx
│           ├── METRO RIO 13082025__b3d8139e.xlsx
│           ├── METRO RIO 13082025__padrao_1__10324624000118__31122024__b3d8139e.xlsx
│           ├── METRO RIO RATING 03112025__0574691f.xlsx
│           ├── METRO SP 23062026__ced52235.xlsx
│           ├── METRO SP 23062026__padrao_3__62070362000106__31122025__ced52235.xlsx
│           ├── METRORIO 30062026__08975c57.xlsx
│           ├── METRORIO 30062026__padrao_3__10324624000118__31122025__08975c57.xlsx
│           ├── MetroRio_06042023__03dfd338.xlsx
│           ├── MetroRio_06042023__padrao_1__10324624000118__31122021__03dfd338.xlsx
│           ├── Metrô São Paulo_06032023__6cf9d7ee.xlsx
│           ├── Metrô São Paulo_06032023__padrao_1__62070362000106__31122021__6cf9d7ee.xlsx
│           ├── MHC PLASTICOS 28072025__43f3c356.xlsx
│           ├── MHC PLASTICOS 28072025__padrao_1__06164824000183__31122024__43f3c356.xlsx
│           ├── MICHELIN RATING 15012026__0b1ac0e1.xlsx
│           ├── MILI RATING 19112025__f36c7985.xlsx
│           ├── MILI RATING 19112025__padrao_2__78908266000124__31122024__f36c7985.xlsx
│           ├── MILI SA 05082025__680fb412.xlsx
│           ├── MINASLIGAS 07052026__8ec8bb49.xlsx
│           ├── MINASLIGAS 07052026__padrao_2__16933590000145__31122024__8ec8bb49.xlsx
│           ├── MINERACAO ONCA PUMA 17082026__f1d0395b.xlsx
│           ├── MINERACAO ONCA PUMA 17082026__padrao_3__48256824000153__31122025__f1d0395b.xlsx
│           ├── MINERACAO ONCA PUMA RATING 03112025__49a9edb7.xlsx
│           ├── MINERACAO ONCA PUMA RATING 03112025__padrao_2__48256824000153__31122024__49a9edb7.xlsx
│           ├── MINERACAO RIO DO NORTE 16062026__82bf6ca2.xlsx
│           ├── MINERACAO RIO DO NORTE 16062026__padrao_3__04932216000146__31122025__82bf6ca2.xlsx
│           ├── MINERACAO RIO DO NORTE SA__ee094deb.xlsx
│           ├── MINERACAO RIO DO NORTE SA__padrao_2__04932216000146__31122024__ee094deb.xlsx
│           ├── MINERACAO USMINAS 13082026__a98f4987.xlsx
│           ├── MINERACAO USMINAS 13082026__padrao_3__12056613000120__31122025__a98f4987.xlsx
│           ├── Mineração Aurizona 17052024__2e989806.xlsx
│           ├── Mineração Aurizona 17052024__padrao_1__42422048000219__31122022__2e989806.xlsx
│           ├── MINERAÇÃO AURIZONA 23082023__fc7f1b71.xlsx
│           ├── MINERAÇÃO AURIZONA 23082023__padrao_1__42422048000138__31122022__fc7f1b71.xlsx
│           ├── MINERAÇÃO PARAGOMINAS - 07082025__647fa294.xlsx
│           ├── MINERAÇÃO PARAGOMINAS - 07082025__padrao_1__12094570000177__31122024__647fa294.xlsx
│           ├── Minerva 01112023__44534d17.xlsx
│           ├── Minerva 01112023__padrao_1__67620377000114__31122022__44534d17.xlsx
│           ├── MINING CORUMBA RATING 28012026__93cf26fa.xlsx
│           ├── MINING CORUMBA RATING 28012026__padrao_2__03327988000196__31122024__93cf26fa.xlsx
│           ├── Moinho Itaipu 29062025__40d11e9f.xlsx
│           ├── Moinho Itaipu 29062025__padrao_1__81716219000193__31122024__40d11e9f.xlsx
│           ├── MOSAIC FERTILIZANTES RATING 21012026__9f2235b2.xlsx
│           ├── MOTIVA 19062026__d6f30655.xlsx
│           ├── MOTIVA RATING 25102025__b645cb18.xlsx
│           ├── MOTIVA RATING 25102025__padrao_2__02846056000197__31122024__b645cb18.xlsx
│           ├── MOTIVA SA 13082026__b75f3e0e.xlsx
│           ├── MOTIVA SA 13082026__padrao_3__02846056000197__31122025__b75f3e0e.xlsx
│           ├── MOTIVA SA 23062026__4e149b24.xlsx
│           ├── Muffato 07112023__ea45a7d0.xlsx
│           ├── Muffato 07112023__padrao_1__76430438000171__31122022__ea45a7d0.xlsx
│           ├── NADIR FIGUEIREDO 02042026__bb12f23d.xlsx
│           ├── NADIR FIGUEIREDO 02042026__padrao_2__61067161000197__31122025__bb12f23d.xlsx
│           ├── NADIR FIGUEIREDO 21072026__e03797de.xlsx
│           ├── NATURAFRIG RATING 20022026__635e86e3.xlsx
│           ├── NATURAFRIG RATING 20022026__padrao_2__18626084000139__31122024__635e86e3.xlsx
│           ├── NC COMUNICACOES RATING 27022026__74987f34.xlsx
│           ├── NEXA 05012026__86b105d8.xlsx
│           ├── NEXA 05012026__padrao_2__42416651000107__86b105d8.xlsx
│           ├── NEXA 08072025__d9ec81d8.xlsx
│           ├── NEXA 08072025__padrao_1__42416651000107__31122024__d9ec81d8.xlsx
│           ├── NEXA RATING 05012026__d98fb6ec.xlsx
│           ├── NEXA RECURSOS MINERAIS 18062026__3c5f365b.xlsx
│           ├── NEXA RECURSOS MINERAIS 18062026__padrao_3__42416651000107__31122025__3c5f365b.xlsx
│           ├── Nitaplast 16_08_2022__889001c2.xlsx
│           ├── Nitaplast 16_08_2022__padrao_1__82295817000107__31122021__889001c2.xlsx
│           ├── NORFIL 13062025__6022f1e6.xlsx
│           ├── NORFIL 13062025__padrao_1__02341494000101__31122024__6022f1e6.xlsx
│           ├── NORFIL 15022024__7ed2fd25.xlsx
│           ├── NORFIL 15022024__padrao_1__02341494000101__31122022__7ed2fd25.xlsx
│           ├── NORFIL SA 27042026__d74bd54d.xlsx
│           ├── NORFIL SA 27042026__padrao_2__02341494000101__31122025__d74bd54d.xlsx
│           ├── NORFIL_13_01_23__0dab96d4.xlsx
│           ├── NORFIL_13_01_23__padrao_1__02341494000101__31122021__0dab96d4.xlsx
│           ├── NOVA FIAÇAO 14052026__01f3499f.xlsx
│           ├── NOVA FIAÇAO 14052026__padrao_2__18067083000100__31122025__01f3499f.xlsx
│           ├── NOVELIS 05062026__0afb3deb.xlsx
│           ├── NOVELIS 05062026__padrao_2__60561800000103__31032026__0afb3deb.xlsx
│           ├── NOVELIS 08052026__7328f258.xlsx
│           ├── NOVELIS 08052026__padrao_2__60561800000103__31032025__7328f258.xlsx
│           ├── NOVO ATACAREJO 28102025__cb6ebbfa.xlsx
│           ├── NOVO ATACAREJO 28102025__padrao_2__20300157003912__31122024__cb6ebbfa.xlsx
│           ├── Oggi Alimentos_13_10_2022__70a7fe9a.xlsx
│           ├── Oggi Alimentos_13_10_2022__padrao_1__01621399000190__31122022__70a7fe9a.xlsx
│           ├── ORIZON 25092025__d945d0e7.xlsx
│           ├── ORIZON 25092025__padrao_1__11421994000136__31122024__d945d0e7.xlsx
│           ├── ORIZON RATING 25112025__9edc1e40.xlsx
│           ├── OXITENO 24062026__a3c848b4.xlsx
│           ├── OXITENO 24062026__padrao_3__62545686000153__31122025__a3c848b4.xlsx
│           ├── PADO_28062023__a76a481b.xlsx
│           ├── PADO_28062023__padrao_1__61144150000678__31122022__a76a481b.xlsx
│           ├── PAPIRUS RATING 25022026__c16ea95e.xlsx
│           ├── PAPIRUS RATING 25022026__padrao_2__60856077000947__31122024__c16ea95e.xlsx
│           ├── PARACATU RATING 04032026__6fc456f5.xlsx
│           ├── PARAGOMINAS 03082026__9cdebf6c.xlsx
│           ├── PARAGOMINAS 03082026__padrao_3__12094570000177__31122025__9cdebf6c.xlsx
│           ├── PARAGOMINAS RATING 18112025__201b39cb.xlsx
│           ├── PARANA BOI 24042026__cae89133.xlsx
│           ├── PARANA BOI 24042026__padrao_2__28969492000147__31122025__cae89133.xlsx
│           ├── Paraná Xisto 13012025__8a645996.xlsx
│           ├── Paraná Xisto 13012025__padrao_1__40254927000172__31122023__8a645996.xlsx
│           ├── Paraná Xisto 22082023__f5474836.xlsx
│           ├── Paraná Xisto 22082023__padrao_1__40254927000172__31122022__f5474836.xlsx
│           ├── PB Gelatinas_03_10_2022__4ca0b278.xlsx
│           ├── PB Gelatinas_03_10_2022__padrao_1__10914514000106__31122021__4ca0b278.xlsx
│           ├── PEROXIDOS 28-04-2026__f4385d57.xlsx
│           ├── PEROXIDOS 28-04-2026__padrao_2__51784262000125__31122025__f4385d57.xlsx
│           ├── Peróxidos_24_02_2023__95ef0097.xlsx
│           ├── Peróxidos_24_02_2023__padrao_1__51784262000125__31122021__95ef0097.xlsx
│           ├── PETROBRAS 10062026__cff13f1b.xlsx
│           ├── PETROBRAS 10062026__padrao_3__33000167000101__31122025__cff13f1b.xlsx
│           ├── PETROBRAS RATING 10112025__1fe799d0.xlsx
│           ├── PETROBRAS RATING 10112025__padrao_2__33000167000101__31122024__1fe799d0.xlsx
│           ├── PETRORECONCAVO 08052026__5bcecadf.xlsx
│           ├── PETRORECONCAVO 08052026__padrao_2__03342704000130__31122025__5bcecadf.xlsx
│           ├── PETRORECONCAVO RATING 11112025__411c3381.xlsx
│           ├── PETRORECONCAVO RATING 11112025__padrao_2__03342704000130__31122024__411c3381.xlsx
│           ├── PLASTICOS AMSTERDAN 13072026__8f8fd868.xlsx
│           ├── PLASTICOS AMSTERDAN 13072026__padrao_3__59221316000156__31122025__8f8fd868.xlsx
│           ├── PM Cascavel__5e9d5c16.xlsx
│           ├── PM Cascavel__padrao_1__76208867000107__31122021__5e9d5c16.xlsx
│           ├── POLIMIX_06062023__9b15ff1d.xlsx
│           ├── POLIMIX_06062023__padrao_1__29067113000196__31122021__9b15ff1d.xlsx
│           ├── POLO FILMS 20-07-2022__d5e79d2c.xlsx
│           ├── POLO FILMS 20-07-2022__padrao_1__26051817000182__31122021__d5e79d2c.xlsx
│           ├── PORTO ITAPOA RATING 10122025__acb727aa.xlsx
│           ├── PORTO ITAPOA RATING 10122025__padrao_2__01317277000105__31122024__acb727aa.xlsx
│           ├── PRATI DONADUZI 14072026__4d2d6a89.xlsx
│           ├── PRATI DONADUZI 14072026__padrao_3__73856593000166__31122025__4d2d6a89.xlsx
│           ├── PRATI DONADUZZI 24082023__814e04eb.xlsx
│           ├── PRATI DONADUZZI 24082023__padrao_1__73856593000166__31122022__814e04eb.xlsx
│           ├── Prati Donaduzzi_24_06_2022__bc11dfc1.xlsx
│           ├── Prati Donaduzzi_24_06_2022__padrao_1__73856593000166__31122021__bc11dfc1.xlsx
│           ├── PRIMA FOODS RATING 27012026__7b6fb90a.xlsx
│           ├── PRIMA FOODS RATING 27012026__padrao_2__16820052000144__31122024__7b6fb90a.xlsx
│           ├── PURO PELLET - Avaliação Middle__79367da9.xlsx
│           ├── PURO PELLET - Avaliação Middle__padrao_1__39449320000169__31122021__79367da9.xlsx
│           ├── QAIR 02072025__43a3728a.xlsx
│           ├── QAIR 02072025__padrao_1__08666285000106__31122024__43a3728a.xlsx
│           ├── QAIR BRASIL RATING 09012026__9419fcda.xlsx
│           ├── Quimica Amparo YPE - Avaliação Middle__33482fb2.xlsx
│           ├── Quimica Amparo YPE - Avaliação Middle__padrao_1__43461789000190__31122021__33482fb2.xlsx
│           ├── RAIZEN 16042026__bc3c6f0d.xlsx
│           ├── RAIZEN_20092023__b4f05f90.xlsx
│           ├── RAIZEN_20092023__padrao_1__08070508000178__31122023__b4f05f90.xlsx
│           ├── RANDON 03082026__bc641aaf.xlsx
│           ├── RANDON 03082026__padrao_3__89086144001198__31122025__bc641aaf.xlsx
│           ├── RANDON 04032024__4d9d311c.xlsx
│           ├── RANDON 04032024__padrao_1__89086144001198__31122022__4d9d311c.xlsx
│           ├── Raízen Geo Biogás 13022025__48909b50.xlsx
│           ├── Raízen Geo Biogás 13022025__padrao_1__25201024000130__31122024__48909b50.xlsx
│           ├── REDE DOR SÃO LUIZ__9a3185e5.xlsx
│           ├── REDE DOR SÃO LUIZ__padrao_1__06047087000139__31122021__9a3185e5.xlsx
│           ├── REFINARIA MATARIPE 17082026__d6e0cfba.xlsx
│           ├── REFINARIA MATARIPE 17082026__padrao_3__41777706000141__31122025__d6e0cfba.xlsx
│           ├── REPINHO 01072025__e76ed1e4.xlsx
│           ├── REPINHO 01072025__padrao_1__82196510000140__31122024__e76ed1e4.xlsx
│           ├── REPINHO 29042025__b9f41461.xlsx
│           ├── REPINHO 29042025__padrao_1__82196510000140__31122023__b9f41461.xlsx
│           ├── RHODIA BRASIL 20072026__42f2e240.xlsx
│           ├── RHODIA BRASIL 20072026__padrao_3__57507626000106__31122025__42f2e240.xlsx
│           ├── RIACHUELO_05072023__878b1ccc.xlsx
│           ├── RIACHUELO_05072023__padrao_1__33200056000149__31122021__878b1ccc.xlsx
│           ├── RIMA INDSUTRIAL 07072025__f98d69cd.xlsx
│           ├── RIMA INDSUTRIAL 07072025__padrao_1__18279158000108__31122024__f98d69cd.xlsx
│           ├── RIMA INDUSTRIAL RATING 04112025__dca15e7f.xlsx
│           ├── RIMA INDUSTRIAL RATING 04112025__padrao_2__18279158000108__31122025__dca15e7f.xlsx
│           ├── Rio de Janeiro Refrescos - Avaliação Mid__3c6016d4.xlsx
│           ├── Rio de Janeiro Refrescos - Avaliação Mid__padrao_1__00074569000100__31122021__3c6016d4.xlsx
│           ├── Rio de Janeiro Refrescos 16102023__6b0a9e01.xlsx
│           ├── Rio de Janeiro Refrescos 16102023__padrao_1__00074569000100__31122022__6b0a9e01.xlsx
│           ├── RIO GALEAO RATING 04112025__8dc9e566.xlsx
│           ├── RIO GALEAO RATING 04112025__padrao_2__19726111000108__31122024__8dc9e566.xlsx
│           ├── RIO PARANÁ ENERGIA 26112024__b5079bd6.xlsx
│           ├── RIO PARANÁ ENERGIA 26112024__padrao_1__23096269000119__31122023__b5079bd6.xlsx
│           ├── ROMI 16052025__e55c2b1c.xlsx
│           ├── ROMI 16052025__padrao_1__56720428001488__31122024__e55c2b1c.xlsx
│           ├── ROMI RATING 31102025__f500bf5f.xlsx
│           ├── ROMI_24062025__caa33e36.xlsx
│           ├── RUY ROCHA 30042026__e08d5886.xlsx
│           ├── RUY ROCHA 30042026__padrao_2__57107609000343__31122024__e08d5886.xlsx
│           ├── RVTRANS 31072026__6a95dac7.xlsx
│           ├── RVTRANS 31072026__padrao_3__32140332000168__31122025__6a95dac7.xlsx
│           ├── SABESP 23062026__252938eb.xlsx
│           ├── SABESP 23062026__padrao_3__43776517000180__31122025__252938eb.xlsx
│           ├── SABESP RATING 10112025__f8b32a3b.xlsx
│           ├── SABESP RATING 10112025__padrao_2__43776517000180__31122024__f8b32a3b.xlsx
│           ├── SABESP_27052025__2f0f7451.xlsx
│           ├── SALOBO METAIS 20082026__6d837be4.xlsx
│           ├── SALOBO METAIS 20082026__padrao_3__33931478000194__31122025__6d837be4.xlsx
│           ├── SALOBO METAIS 28072025__706c5c71.xlsx
│           ├── SALOBO METAIS 28072025__padrao_1__33931478000194__31122024__706c5c71.xlsx
│           ├── SALOBO METAIS RATING 12112025__2d61b43a.xlsx
│           ├── SAMARCO 13102025__ed4b5b08.xlsx
│           ├── SAMARCO 13102025__padrao_2__16628281000161__ed4b5b08.xlsx
│           ├── SAMARCO 16102023__31ef524c.xlsx
│           ├── SAMARCO 16102023__padrao_1__16628281000161__31122022__31ef524c.xlsx
│           ├── SAMARCO 21082026__76f0a669.xlsx
│           ├── SAMARCO 21082026__padrao_3__16628281000161__31122025__76f0a669.xlsx
│           ├── SAMARCO 25082025__7fd64bc5.xlsx
│           ├── SAMARCO RATING 23122025__9e9328fb.xlsx
│           ├── SAMARCO RATING 23122025__padrao_2__16628281000161__31122024__9e9328fb.xlsx
│           ├── SANEAGO_20250106__2aa099e7.xlsx
│           ├── SANEAGO_20250106__padrao_1__01616929000102__31122023__2aa099e7.xlsx
│           ├── SANEPAR 02072025__267c8562.xlsx
│           ├── SANEPAR 02072025__padrao_1__76484013000145__31122024__267c8562.xlsx
│           ├── SANEPAR 12012024__72666602.xlsx
│           ├── SANEPAR 12012024__padrao_1__76484013000145__31122022__72666602.xlsx
│           ├── SANEPAR 21052026__20cbb585.xlsx
│           ├── SANEPAR 21052026__padrao_2__76484013000145__31122025__20cbb585.xlsx
│           ├── SANEPAR RATING 17102025__0aa103a9.xlsx
│           ├── SANEPAR RATING 17102025__padrao_2__76484013000145__0aa103a9.xlsx
│           ├── SANSUY 10062025 v2__d21b295c.xlsx
│           ├── SANSUY 10062025 v2__padrao_1__14807945000124__31122024__d21b295c.xlsx
│           ├── SANSUY 10062025__240c892a.xlsx
│           ├── Santa Maria_11_03_2022__9349f339.xlsx
│           ├── Santa Maria_11_03_2022__padrao_1__77887917000184__31122021__9349f339.xlsx
│           ├── Santa Terezinha 24032025__edf2b7ad.xlsx
│           ├── Santa Terezinha 24032025__padrao_1__79109237000165__31122024__edf2b7ad.xlsx
│           ├── SANTAHELENA_2023_03_15__a5ffc848.xlsx
│           ├── SANTAHELENA_2023_03_15__padrao_1__59970947000178__31122021__a5ffc848.xlsx
│           ├── Santander 02012024__35fd824c.xlsx
│           ├── Santher 01022024 sem eprotocolo__3432eec2.xlsx
│           ├── Santher 01022024 sem eprotocolo__padrao_1__61101895000145__31122022__3432eec2.xlsx
│           ├── Santo Antonio Energia 01102024__db767191.xlsx
│           ├── Santo Antonio Energia 01102024__padrao_1__09391823000240__31122023__db767191.xlsx
│           ├── SAO MARTINHO 01062026__115501fa.xlsx
│           ├── SAO MARTINHO 01062026__padrao_2__51466860000156__31032026__115501fa.xlsx
│           ├── SAO MARTINHO RATING 02022026__81e28dcb.xlsx
│           ├── SAO MARTINHO RATING 02022026__padrao_2__51466860000156__31032025__81e28dcb.xlsx
│           ├── SAVOY MATRIZ 27042026__1c43267a.xlsx
│           ├── SCALA DATA CENTERS 0508226__1d63ec4b.xlsx
│           ├── SCALA DATA CENTERS 0508226__padrao_3__34562112000158__31122025__1d63ec4b.xlsx
│           ├── SCALA DATA CENTERS 2025__2ae4249c.xlsx
│           ├── SCALA DATA CENTERS 2025__padrao_1__34562112000158__31122024__2ae4249c.xlsx
│           ├── SCALA DATA CENTERS RATING 18112025__a67a8f86.xlsx
│           ├── SCHULZ 18082026__4d8afcb7.xlsx
│           ├── SCHULZ 18082026__padrao_3__84693183000168__31122025__4d8afcb7.xlsx
│           ├── Segalas Alimentos - Avaliação Middle__90931f64.xlsx
│           ├── Segalas Alimentos - Avaliação Middle__padrao_1__01333984000195__31122021__90931f64.xlsx
│           ├── SENDAS DISTRIBUIDORA 22_08_2022__8bd1bbc1.xlsx
│           ├── SENDAS DISTRIBUIDORA 22_08_2022__padrao_1__06057223000171__31122021__8bd1bbc1.xlsx
│           ├── SERLONAS RATING 10032026__a1dd608f.xlsx
│           ├── SERLONAS RATING 10032026__padrao_2__04630268000168__31122025__a1dd608f.xlsx
│           ├── SERRANA 11062025__d3346017.xlsx
│           ├── SERRANA 11062025__padrao_1__07094597000120__31122024__d3346017.xlsx
│           ├── SERVENG CIVILSAN 18082026__90ee3480.xlsx
│           ├── SERVENG CIVILSAN 18082026__padrao_3__48540421000131__31122025__90ee3480.xlsx
│           ├── SERVENG CIVILSAN RATING 12112025__d00caae3.xlsx
│           ├── SERVENG CIVILSAN RATING 12112025__padrao_2__48540421000131__31122024__d00caae3.xlsx
│           ├── SHOPPING BOULEVARD RATING 16032026__d7120e4b.xlsx
│           ├── SHOPPING BOULEVARD RATING 16032026__padrao_2__28547761000187__31122024__d7120e4b.xlsx
│           ├── SHOPPING VILHA  VELHA RATING 19032026__66dbf66d.xlsx
│           ├── SHOPPING VILHA  VELHA RATING 19032026__padrao_2__15091769000130__31122024__66dbf66d.xlsx
│           ├── SINOBRAS 09072026__0a7ed7f4.xlsx
│           ├── SINOBRAS 09072026__padrao_3__07933914000154__31122025__0a7ed7f4.xlsx
│           ├── SLC_AGRICOLA_23_11_2022__f94f457d.xlsx
│           ├── SLC_AGRICOLA_23_11_2022__padrao_1__89096457000155__31122021__f94f457d.xlsx
│           ├── SOFTYS BRASIL 25062025__ef29230d.xlsx
│           ├── SOFTYS BRASIL 25062025__padrao_1__44145845000140__31122024__ef29230d.xlsx
│           ├── SOFTYS BRASIL RATING 03122025__260b7011.xlsx
│           ├── SOFTYS_09_03_2022__32aa8a21.xlsx
│           ├── SOFTYS_09_03_2022__padrao_1__44145845000140__31122020__32aa8a21.xlsx
│           ├── SOLAR BEBIDAS SA RATING 09012026__d0a958ae.xlsx
│           ├── SOLAR BEBIDAS SA RATING 09012026__padrao_2__41052420000107__31122024__d0a958ae.xlsx
│           ├── SOLAR BR 25052026__a891ce48.xlsx
│           ├── SOLAR BR 25052026__padrao_2__41501877000143__31122025__a891ce48.xlsx
│           ├── SOLAR BR ENERGIA RATING 09012026__d39a75ce.xlsx
│           ├── SOLAR BR ENERGIA RATING 09012026__padrao_2__41501877000143__31122024__d39a75ce.xlsx
│           ├── SOLAR ENERGIAS RATING 12122025__3ca8ece2.xlsx
│           ├── SOLAR ENERGIAS RATING 12122025__padrao_2__41501877000143__3ca8ece2.xlsx
│           ├── SOLVI ESSENCIS RATING 23032026__0eb99c86.xlsx
│           ├── SOLVI ESSENCIS RATING 23032026__padrao_2__40263170000183__31122024__0eb99c86.xlsx
│           ├── SONORA ESTANCIA 25052026__cff9298d.xlsx
│           ├── SONORA ESTANCIA 25052026__padrao_2__47902283000120__31032025__cff9298d.xlsx
│           ├── SOUTH32 18082026__571c356d.xlsx
│           ├── SOUTH32 18082026__padrao_3__42105890000146__30062025__571c356d.xlsx
│           ├── SOUTH32 RATING 09122025__8b486903.xlsx
│           ├── SOUZA CRUZ RATING 04032026__ab558a28.xlsx
│           ├── SOUZA CRUZ RATING 04032026__padrao_2__33009911000139__31122024__ab558a28.xlsx
│           ├── spal 05032024__e9e09a23.xlsx
│           ├── spal 05032024__padrao_1__61186888000193__31122022__e9e09a23.xlsx
│           ├── Sta Casa Rio Claro 17102023__d60f205e.xlsx
│           ├── Sta Casa Rio Claro 17102023__padrao_1__56384183000140__31122022__d60f205e.xlsx
│           ├── Stara - Avaliação Middle__f7a75664.xlsx
│           ├── Stara - Avaliação Middle__padrao_1__91495499000100__31122021__f7a75664.xlsx
│           ├── SUDATI 08042024__1fb6be36.xlsx
│           ├── SUDATI 08042024__padrao_1__08803452000113__31122022__1fb6be36.xlsx
│           ├── Sumitomo_10082023__5d63d739.xlsx
│           ├── Sumitomo_10082023__padrao_1__13816470000170__31122022__5d63d739.xlsx
│           ├── SUPERMERCADO LIS RATING 29012026__cbac6982.xlsx
│           ├── SUPERMERCADO LIS RATING 29012026__padrao_2__07255463000143__31122024__cbac6982.xlsx
│           ├── Supremo Cimentos_02032023__e33a0665.xlsx
│           ├── Supremo Cimentos_02032023__padrao_1__05798883000140__31122021__e33a0665.xlsx
│           ├── Suzano 01022024 sem eprotocolo__e4e77d90.xlsx
│           ├── Suzano 01022024 sem eprotocolo__padrao_1__16404287000155__31122023__e4e77d90.xlsx
│           ├── SUZANO 29052026__6796f705.xlsx
│           ├── SUZANO 29052026__padrao_2__16404287000155__31122025__6796f705.xlsx
│           ├── SUZANO RATING 03122025__2d082e4e.xlsx
│           ├── SUZANO RATING 03122025__padrao_2__16404287000155__31122024__2d082e4e.xlsx
│           ├── SUZANO_2023_07_03__d3b48d04.xlsx
│           ├── SUZANO_2023_07_03__padrao_1__16404287000155__31122022__d3b48d04.xlsx
│           ├── SUZANO_26062025__a893d58a.xlsx
│           ├── SYLVAMO_20_07_2022__ab119e6e.xlsx
│           ├── SYLVAMO_20_07_2022__padrao_1__52736949000158__31122021__ab119e6e.xlsx
│           ├── SÃO PAULO ENERGÉTICA 11062025__9d099715.xlsx
│           ├── SÃO PAULO ENERGÉTICA 11062025__padrao_1__07726782000190__31122024__9d099715.xlsx
│           ├── TCP 04082025__e04db3bc.xlsx
│           ├── TCP 04082025__padrao_1__12919786000124__31122024__e04db3bc.xlsx
│           ├── TCP RATING 04112025__0006d6f3.xlsx
│           ├── TCP RATING 04112025__padrao_2__12919786000124__04112025__0006d6f3.xlsx
│           ├── TCP_Paranaguá_16_01_2023__151f3305.xlsx
│           ├── TCP_Paranaguá_16_01_2023__padrao_1__12919786000124__31122021__151f3305.xlsx
│           ├── TECPAR 03072024__853f15d0.xlsx
│           ├── TECPAR 03072024__padrao_1__77964393000188__01042024__853f15d0.xlsx
│           ├── TEREOS ACUCAR 14072026__f90c07c5.xlsx
│           ├── TEREOS ACUCAR 14072026__padrao_3__47080619000117__31032026__f90c07c5.xlsx
│           ├── TEREOS AMIDOS E ADOCANTES RATING 2711202__d468ff74.xlsx
│           ├── TEREOS AMIDOS E ADOCANTES RATING 2711202__padrao_2__65882680000160__31122025__d468ff74.xlsx
│           ├── TEREOS AÇÚCAR RATING 25032026__645c3bb7.xlsx
│           ├── TEREOS AÇÚCAR RATING 25032026__padrao_2__47080619000117__31032025__645c3bb7.xlsx
│           ├── Termomecânica São Paulo_05102023__870f2511.xlsx
│           ├── Termomecânica São Paulo_05102023__padrao_1__59106666000171__31122022__870f2511.xlsx
│           ├── TERNIUM 26052026__c7268245.xlsx
│           ├── TERNIUM 26052026__padrao_2__07005330000119__31122025__c7268245.xlsx
│           ├── TERNIUM BRASIL 02072025__3a057aa1.xlsx
│           ├── TERNIUM BRASIL 02072025__padrao_1__07005330000119__31122024__3a057aa1.xlsx
│           ├── TERNIUM RATING 27102025__e80da3b9.xlsx
│           ├── Terphane - Avaliação Middle__7e289507.xlsx
│           ├── Terphane - Avaliação Middle__padrao_1__02429732000127__31122021__7e289507.xlsx
│           ├── TERPHANE RATING 30012026__18b44cd7.xlsx
│           ├── TERPHANE RATING 30012026__padrao_2__02429732000127__31122024__18b44cd7.xlsx
│           ├── TES Terminal Exp Santos 05052026__832fb961.xlsx
│           ├── TES Terminal Exp Santos 05052026__padrao_2__18845076000183__31122025__832fb961.xlsx
│           ├── TIGRE_27032023__ec8b81af.xlsx
│           ├── TIGRE_27032023__padrao_1__84684455000163__31122021__ec8b81af.xlsx
│           ├── TIM - Avaliação Middle__1862aeb4.xlsx
│           ├── TIM - Avaliação Middle__padrao_1__02421421000111__31122021__1862aeb4.xlsx
│           ├── TODIMO_06122024__f0c78640.xlsx
│           ├── TODIMO_06122024__padrao_1__15375991000164__31122023__f0c78640.xlsx
│           ├── TRANSPETRO 08062026__b100b981.xlsx
│           ├── TRANSPETRO 08062026__padrao_3__02709449000159__31122025__b100b981.xlsx
│           ├── TRANSPETRO 09072025__d86cfd1c.xlsx
│           ├── TRANSPETRO 09072025__padrao_1__02709449000159__31122024__d86cfd1c.xlsx
│           ├── TRANSPETRO 25082025__3e8e79aa.xlsx
│           ├── TRANSPETRO 25082025_consiste__69cac8a2.xlsx
│           ├── TRANSPETRO RATING 19112025__6ab67a68.xlsx
│           ├── TRANSPPASS 03082026__5da752c3.xlsx
│           ├── TRANSPPASS 03082026__padrao_3__06268099000193__31122025__5da752c3.xlsx
│           ├── TRANSVIDA RATING 20022026__ebf06f26.xlsx
│           ├── TRANSVIDA RATING 20022026__padrao_2__33443024000174__31122024__ebf06f26.xlsx
│           ├── TRENS DE SP 21082025__dce7cff5.xlsx
│           ├── TRENS DE SP 21082025__padrao_1__42288184000187__31122024__dce7cff5.xlsx
│           ├── TROMBINI - 15.07.2024__68ca077f.xlsx
│           ├── TROMBINI - 15.07.2024__padrao_1__11252642000102__31122023__68ca077f.xlsx
│           ├── TROMBINI 28082023__8b30b31b.xlsx
│           ├── TROMBINI 28082023__padrao_1__11252642000102__31122022__8b30b31b.xlsx
│           ├── Trombini_10_11_2022__5f37c16e.xlsx
│           ├── Trombini_10_11_2022__padrao_1__11252642000102__31122021__5f37c16e.xlsx
│           ├── TUPY 14072025__0f77b00a.xlsx
│           ├── TUPY 14072025__padrao_1__84683374000149__31122024__0f77b00a.xlsx
│           ├── TUPY RATING 19112025__b11f1685.xlsx
│           ├── TUPY_15052023__302cbbb9.xlsx
│           ├── TUPY_15052023__padrao_1__84683374000149__31122021__302cbbb9.xlsx
│           ├── UHE SAO SIMAO 28082025__9efd37d4.xlsx
│           ├── UHE SAO SIMAO 28082025__padrao_1__27352303000120__31122024__9efd37d4.xlsx
│           ├── UNIAO OESTE 20052026__952a4896.xlsx
│           ├── UNIAO OESTE 20052026__padrao_2__81270548000153__31122025__952a4896.xlsx
│           ├── UNIDAS SUL 180052026__42427791.xlsx
│           ├── UNIDAS SUL 180052026__padrao_2__07718633000189__31122025__42427791.xlsx
│           ├── UNIGEL - Proquigel 30-01-2023__671e6046.xlsx
│           ├── UNIGEL - Proquigel 30-01-2023__padrao_1__27515154002035__31122021__671e6046.xlsx
│           ├── UNIGEL 24072025__50daf92c.xlsx
│           ├── UNIGEL 24072025__padrao_1__38246958000130__31122024__50daf92c.xlsx
│           ├── Unilever_17112023__7f7e312d.xlsx
│           ├── Unilever_17112023__padrao_1__01615814000101__31122022__7f7e312d.xlsx
│           ├── UNIMED 15072026__31b53d33.xlsx
│           ├── UNIMED 15072026__padrao_3__77781706000243__31122025__31b53d33.xlsx
│           ├── UNIMED LONDRINA__0c3aa35f.xlsx
│           ├── UNIMED LONDRINA__padrao_3__75222224000147__31122025__0c3aa35f.xlsx
│           ├── UNIPAR 19052026__42d746df.xlsx
│           ├── UNIPAR 19052026__padrao_2__33958695000178__31122025__42d746df.xlsx
│           ├── UNIPAR RATING 04112025__2a408a23.xlsx
│           ├── UNIPAR RATING 04112025__padrao_2__33958695000178__31122024__2a408a23.xlsx
│           ├── UNIRON_10_10_2022__0c10ed88.xlsx
│           ├── UNIRON_10_10_2022__padrao_1__03327149000178__31122021__0c10ed88.xlsx
│           ├── União Química 14112023__b0bfc58c.xlsx
│           ├── União Química 14112023__padrao_1__60665981000118__31122022__b0bfc58c.xlsx
│           ├── URUCUIA GERAÇÃO 20082025__8ba73e98.xlsx
│           ├── USIMINAS 07072025__7f71a572.xlsx
│           ├── USIMINAS 07072025__padrao_1__60894730000105__31122024__7f71a572.xlsx
│           ├── USIMINAS 15042026__fce349a8.xlsx
│           ├── USIMINAS 15042026__padrao_2__42956441000101__31122024__fce349a8.xlsx
│           ├── USIMINAS 25062026__4d2af823.xlsx
│           ├── USIMINAS 25062026__padrao_3__60894730000105__31122025__4d2af823.xlsx
│           ├── USIMINAS RATING 05112025__ba72010b.xlsx
│           ├── USINA LATICIÍNIOS JUSSARA 08052026__6c69c7c8.xlsx
│           ├── USINA LATICIÍNIOS JUSSARA 08052026__padrao_2__47964911000100__31122025__6c69c7c8.xlsx
│           ├── USINAGEM TIMBO RATING 05022026__74987f34.xlsx
│           ├── V.TAL RATING 31102025__ceef233e.xlsx
│           ├── V.TAL RATING 31102025__padrao_2__02041460000193__31122024__ceef233e.xlsx
│           ├── VALE 20072026__31a7704d.xlsx
│           ├── VALE 30-05-2025__d96b8c37.xlsx
│           ├── VALE 30-05-2025__padrao_1__33592510000154__31122024__d96b8c37.xlsx
│           ├── VALE RATING 04112025__738c2ea2.xlsx
│           ├── VALGROUP PACKAGING SOLUTIONS - Avaliação__ca9dc25e.xlsx
│           ├── VALGROUP PACKAGING SOLUTIONS - Avaliação__padrao_1__32184195000163__31122021__ca9dc25e.xlsx
│           ├── VALLOUREC SOLUCOES RATING 08012026__09ded324.xlsx
│           ├── VALLOUREC SOLUCOES RATING 08012026__padrao_2__08689024000101__31122024__09ded324.xlsx
│           ├── VALLOUREC TUBOS RATING 08012025__e1278c9e.xlsx
│           ├── VALLOUREC TUBOS RATING 08012025__padrao_2__17170150000146__e1278c9e.xlsx
│           ├── VEOLIA_28082024__d15f1da6.xlsx
│           ├── VEOLIA_28082024__padrao_1__02740510000120__31122023__d15f1da6.xlsx
│           ├── VERALLIA_02_12_2022__570311a7.xlsx
│           ├── VERALLIA_02_12_2022__padrao_1__60853942000144__31122021__570311a7.xlsx
│           ├── VIBRA 26.07.2024__11f9c65f.xlsx
│           ├── VIBRA 26.07.2024__padrao_1__93586303000119__31122023__11f9c65f.xlsx
│           ├── VIBRA_05092025__58615936.xlsx
│           ├── VIBRA_05092025__padrao_1__93586303000119__31122024__58615936.xlsx
│           ├── VIDROPORTO RATING 03022026__be2945fc.xlsx
│           ├── VIDROPORTO RATING 03022026__padrao_2__48845556000105__31122025__be2945fc.xlsx
│           ├── VILLARES METALS 02072026__a77923b4.xlsx
│           ├── VILLARES METALS 02072026__padrao_3__42566752000164__31032026__a77923b4.xlsx
│           ├── VILLARES METALS RATING 12112025__5d160aae.xlsx
│           ├── VILLARES METALS RATING 12112025__padrao_2__42566752000164__31032025__5d160aae.xlsx
│           ├── VILLARES_14032023__941054e8.xlsx
│           ├── VILLARES_14032023__padrao_1__42566752000164__31122021__941054e8.xlsx
│           ├── VIPAL_05042023__33c3c759.xlsx
│           ├── VIPAL_05042023__padrao_1__87870952000144__31122022__33c3c759.xlsx
│           ├── VIRACOPOS - 04042024__3cff52a2.xlsx
│           ├── VIRACOPOS - 04042024__padrao_1__14522178000107__31122023__3cff52a2.xlsx
│           ├── Vista Foods 15122023__b96e1a12.xlsx
│           ├── Vista Foods 15122023__padrao_1__50615144000120__b96e1a12.xlsx
│           ├── Vitopel_2023_07_27__68c4a33e.xlsx
│           ├── Vitopel_2023_07_27__padrao_1__03206039000158__31122021__68c4a33e.xlsx
│           ├── VIVIX 28_07_2022__2351215a.xlsx
│           ├── VIVIX 28_07_2022__padrao_1__10858291000107__31122021__2351215a.xlsx
│           ├── Volks 21-07-2022__2ab56d9e.xlsx
│           ├── Volks 21-07-2022__padrao_1__59104422000150__31122021__2ab56d9e.xlsx
│           ├── VOLKSWAGEN RATING 08012026__cbc03e4a.xlsx
│           ├── VOTORANTIM 07072025__939cc975.xlsx
│           ├── VOTORANTIM 07072025__padrao_1__03407049000151__31122024__939cc975.xlsx
│           ├── VOTORANTIM 07072026__c57d0810.xlsx
│           ├── VOTORANTIM 07072026__padrao_3__03407049000151__31122025__c57d0810.xlsx
│           ├── VOTORANTIM CIMENTOS RATING__d3bd5b7c.xlsx
│           ├── VOTORANTIM NNE 20082025__51733d10.xlsx
│           ├── VOTORANTIM NNE 20082025__padrao_1__10656452000180__31122024__51733d10.xlsx
│           ├── VOTORANTIM NNE 20082025_consiste__b22b8a5d.xlsx
│           ├── VOTORANTIM NNE RATING 22122025__78794b3e.xlsx
│           ├── VOTORANTIM RATING 05112025__27158ef8.xlsx
│           ├── VOTORANTIM SA 11052026__6f4f4ac1.xlsx
│           ├── VOTORANTIM SA 11052026__padrao_2__01637895000132__31122025__6f4f4ac1.xlsx
│           ├── Votorantim__5faaff79.xlsx
│           ├── Votorantim__padrao_1__01637895000132__31122021__5faaff79.xlsx
│           ├── VTAL Rede Neutra 23072025__e9195188.xlsx
│           ├── VW do Brasil_18072023__15a9ef87.xlsx
│           ├── VW do Brasil_18072023__padrao_1__59104422000150__31122022__15a9ef87.xlsx
│           ├── WD AGROINDUSTRIAL 20052026__99b02258.xlsx
│           ├── WD AGROINDUSTRIAL 20052026__padrao_2__01105558000102__31122024__99b02258.xlsx
│           ├── WEG - MATRIZ 15052026__c92634c5.xlsx
│           ├── WEG - MATRIZ 15052026__padrao_2__07175725000160__31122025__c92634c5.xlsx
│           ├── WEG 03072025__90d97390.xlsx
│           ├── WEG 03072025__padrao_1__07175725000160__31122024__90d97390.xlsx
│           ├── WEG 11012024__052f2a15.xlsx
│           ├── WEG 11012024__padrao_1__07175725000160__31122022__052f2a15.xlsx
│           ├── WEG 25112024__7ddd0920.xlsx
│           ├── WEG 25112024__padrao_1__07175725000160__31122023__7ddd0920.xlsx
│           ├── WEG RATING 04112025__602fe011.xlsx
│           ├── WHB_08042024__f0b4f6fc.xlsx
│           ├── WHB_08042024__padrao_1__01261681000104__31122022__f0b4f6fc.xlsx
│           ├── WHB_11042024__c7d56488.xlsx
│           ├── WHB_11042024__padrao_1__01261681000104__31122023__c7d56488.xlsx
│           ├── WHIRLPOOL_24_04_2023__8e290f27.xlsx
│           ├── WHIRLPOOL_24_04_2023__padrao_1__59105999000186__31122021__8e290f27.xlsx
│           ├── WHITE MARTINS 20082025__ad62bb6e.xlsx
│           ├── WHITE MARTINS 20082025__padrao_1__35820448000136__31122024__ad62bb6e.xlsx
│           ├── WHITE MARTINS 30072026__a26b186f.xlsx
│           ├── WHITE MARTINS 30072026__padrao_3__35820448000136__31122025__a26b186f.xlsx
│           ├── WHITE MARTINS RATING 30102025__5835ba83.xlsx
│           ├── YARA 13072026__e53ff968.xlsx
│           ├── YARA NITROGENADOS RATING 11112025__d03ac06a.xlsx
│           ├── YARA NITROGENADOS RATING 11112025__padrao_2__92660604016933__31122024__d03ac06a.xlsx
│           └── ZILOR 27052026__c2ec63c5.xlsx
├── scripts/
│   ├── auditoria_fase3_alertas.py
│   ├── busca_lucro_liquido.py
│   ├── busca_profunda.py
│   ├── buscar_coordenadas_amostra.py
│   ├── captura_evidencias.py
│   ├── check_fase2.py
│   ├── comparar_bases.py
│   ├── debug_silver_comercializadoras.py
│   ├── debug_zero_consumidores.py
│   ├── find_coords.py
│   ├── find_labels.py
│   ├── restore_data_calculo.py
│   ├── sync_metadata.py
│   ├── teste_antes_depois_semantica.py
│   ├── teste_hipotese_cluster.py
│   └── valida_ajustes.py
├── src/
│   ├── app/
│   │   ├── comercializadoras/
│   │   │   └── orquestrador_comercializadoras.py
│   │   ├── consumidores/
│   │   │   └── orquestrador_consumidores.py
│   │   ├── __init__.py
│   │   ├── bootstrap.py
│   │   ├── config_builder.py
│   │   └── context.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── rodar_fichas_comercializadoras.py
│   │   └── rodar_fichas_consumidores.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── dados.py
│   │   ├── datas.py
│   │   ├── dominio.py
│   │   ├── excel.py
│   │   ├── hashing.py
│   │   ├── identificadores.py
│   │   ├── json.py
│   │   ├── nulos.py
│   │   ├── numeros.py
│   │   ├── paths.py
│   │   ├── servico_desduplicacao.py
│   │   ├── texto.py
│   │   └── utils_orquestracao.py
│   ├── control/
│   │   ├── __init__.py
│   │   ├── carregador_de_mapeamento.py
│   │   ├── layout_catalog.py
│   │   ├── logger.py
│   │   └── quality_loader.py
│   ├── domain/
│   │   ├── auditoria/
│   │   │   ├── __init__.py
│   │   │   └── servico_auditoria.py
│   │   ├── cadastro/
│   │   │   ├── __init__.py
│   │   │   ├── servico_bureau.py
│   │   │   └── servico_receita.py
│   │   ├── carga_manual/
│   │   │   ├── __init__.py
│   │   │   ├── servico_carga_manual.py
│   │   │   └── servico_repescagem.py
│   │   ├── consumidores/
│   │   │   └── classificacao.py
│   │   ├── contrapartes/
│   │   │   ├── __init__.py
│   │   │   ├── segmentacao.py
│   │   │   └── servico_enquadramento.py
│   │   ├── contratos/
│   │   │   ├── __init__.py
│   │   │   └── servico_contratos_denodo.py
│   │   ├── credito/
│   │   │   ├── __init__.py
│   │   │   ├── motor_ead.py
│   │   │   ├── motor_lgd.py
│   │   │   ├── motor_pe.py
│   │   │   ├── motor_taxa_risco.py
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
│   │   │   ├── rating.py
│   │   │   ├── score_qualitativo.py
│   │   │   ├── score_quantitativo.py
│   │   │   ├── score_total.py
│   │   │   └── servico_override.py
│   │   ├── diagnostico/
│   │   │   ├── servico_diagnostico.py
│   │   │   ├── servico_exportacao.py
│   │   │   └── servico_recuperacao.py
│   │   ├── fichas/
│   │   │   ├── __init__.py
│   │   │   ├── derivador_financeiro.py
│   │   │   ├── extrator.py
│   │   │   └── validador.py
│   │   ├── garantias/
│   │   │   ├── __init__.py
│   │   │   └── servico_garantia.py
│   │   ├── mtm/
│   │   │   ├── __init__.py
│   │   │   └── servico_mtm.py
│   │   ├── salesforce/
│   │   │   ├── __init__.py
│   │   │   └── servico_salesforce.py
│   │   ├── __init__.py
│   │   └── enums.py
│   ├── gold/
│   │   ├── __init__.py
│   │   ├── regras_gold.py
│   │   └── servico_gold.py
│   ├── relational/
│   │   ├── dimensions/
│   │   │   ├── __init__.py
│   │   │   └── dim_contraparte.py
│   │   └── facts/
│   │       ├── __init__.py
│   │       ├── fato_alerta_util.py
│   │       ├── fato_alertas.py
│   │       ├── fato_alertas_manuais.py
│   │       ├── fato_analise_credito.py
│   │       ├── fato_exposicao_risco.py
│   │       ├── fato_garantia.py
│   │       ├── fato_reconciliacao_contrato_mtm.py
│   │       └── fato_reconciliacao_fichas_salesforce.py
│   ├── services/
│   │   ├── connectors/
│   │   │   ├── __init__.py
│   │   │   ├── denodo_connector.py
│   │   │   ├── mtm_connector.py
│   │   │   ├── receita_connector.py
│   │   │   ├── risk3_connector.py
│   │   │   └── salesforce_connector.py
│   │   └── __init__.py
│   ├── silver/
│   │   ├── __init__.py
│   │   ├── documentos_classificados.py
│   │   ├── formatador_silver.py
│   │   └── mapeador_dominio.py
│   ├── staging/
│   │   ├── __init__.py
│   │   ├── descoberta.py
│   │   └── staging_arquivo.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── armazenamento_manifest.py
│   │   ├── bronze_arquivo.py
│   │   ├── escrever_dados.py
│   │   ├── estado_armazenamento.py
│   │   └── operacao_arquivo.py
│   └── ui/
│       ├── views/
│       │   ├── visao_carga_manual.py
│       │   ├── visao_carteira.py
│       │   ├── visao_orquestrador.py
│       │   └── visao_silver.py
│       └── app.py
├── .gitignore
├── gerar_contexto_ia.py
├── main.py
├── README.md
└── reset.py
