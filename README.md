# EyesBot
 Le bot de trading accessible a tous 


# Liste des commandes pour set-up le projet:

# Clonage du repo:

>git clone https://github.com/EyesWatch/EyesBot.git

Instalation des pre requis/dependance

>bash ./EyesBot/install.sh

Ajout des comptes:

>nano EyesBot/secret.json

# Commande d'Éxecution des bots:
Super reversal:

>python3 EyesBot/strategies/super_reversal/strategy_multi.py

Grid trading:

>python3 EyesBot/strategies/grid_spot_usd/strategy.py

Alligator:

>python3 EyesBot/strategies/Alligator/Alligator.py

AlliPerpETH:

>python3 EyesBot/strategies/AlliPerp/AlliPerpETH.py

AlliPerpBTC:

>python3 EyesBot/strategies/AlliPerp/AlliPerpBTC.py

CrossEMA+RSI:

>python3 EyesBot/strategies/CrossEMA+RSI/CrossEMA+RSI.py

Trix:

>python3 EyesBot/strategies/Trix/Trix.py

BigWillv2:

>python3 EyesBot/strategies/BigWillv2/Bigwillv2.py

# Automatisation du processus
ouvrir le crontab:

>crontab -e 
>1

Site pour timer : https://crontab.guru

# Ajout code d'execution dans le crontab:

Super Reversal ( 1h ):

>0 * * * * python3 EyesBot/strategies/super_reversal/strategy_multi.py >> cronlog.log

Grid Trading ( toute les 5 min ):

>*/5 * * * * python3 EyesBot/strategies/grid_spot_usd/strategy.py >> cronlog.log

Alligator (1h):

>0 * * * * python3 EyesBot/strategies/Alligator/Alligator.py >> cronlog.log

AlliPerpETH (1h):

>0 * * * * python3 EyesBot/strategies/AlliPerp/AlliPerpETH.py >> cronlog.log

AlliPerpBTC (1h):

>0 * * * * python3 EyesBot/strategies/AlliPerp/AlliPerpBTC.py >> cronlog.log

CrossEMA+RSI (1h):

>0 * * * * python3 EyesBot/strategies/CrossEMA+RSI/CrossEMA+RSI.py >> cronlog.log

Trix (1h):

>0 * * * * python3 EyesBot/strategies/Trix/Trix.py >> cronlog.log


BigWillv2 (1h):

>0 * * * * python3 EyesBot/strategies/BigWillv2/Bigwillv2.py >> cronlog.log



# Secret.json
Pour ajouter plus de compte -> Modifier "New_Account_Name" a la fin du fichier secret.json

