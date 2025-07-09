# 리소스 그룹 생성
#az group create --name user23-rg --location eastus2


# SQL Server
az sql server create --name aidbtune --resource-group user23-RG --location eastus2 --admin-user saadmin --admin-password SAaidbAD123!

# SQL Database (Standard S0)
az sql db create --resource-group user23-RG --server aidbtune --name aidbtuneDB --service-objective S0

# 방화벽 규칙 (자신의 IP 허용)
az sql server firewall-rule create --resource-group user23-RG --server aidbtune --name AllowYourIP --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0

# Azure AI Search 서비스 생성
az search service create --name aidbsearch --resource-group user23-RG --location eastus2 --sku standard

# Azure OpenAI 리소스 생성
az cognitiveservices account create --name aidbopenai --resource-group user23-RG --location eastus2 --kind OpenAI --sku S0 --yes --custom-domain ""

# Azure OPEnAI 리소스 soft-delete 되어서 purge 후 재생성
az cognitiveservices account purge --name aidbopenai --resource-group user23-RG


# 생성되 리소스 확인
# echo "✅ Azure SQL Server: $SQL_SERVER_NAME"
# echo "✅ Azure SQL Admin User: $SQL_ADMIN_USER"
# echo "✅ Azure SQL Database: $SQL_DB_NAME"
# echo "✅ Azure AI Search: $SEARCH_SERVICE_NAME"
# echo "✅ Azure OpenAI: $OPENAI_NAME"


#Azure SQL Database 연결 문자열
# echo "Server=tcp:aidbtune.database.windows.net,1433;Initial Catalog=$SQL_DB_NAME;Persist Security Info=False;User ID=saadmin;Password=saadmin;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"


# #Azure Search Admin Key 조회
# az search admin-key show --service-name $SEARCH_SERVICE_NAME --resource-group $RESOURCE_GROUP


# #OpenAI Key 조회
# az cognitiveservices account keys list --name $OPENAI_NAME --resource-group $RESOURCE_GROUP

