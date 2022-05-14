# EyesBot
 Le bot de trading accessible a tous 

Account1 = Super reversal

Account2 = Grid Trading

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

# Secret.json
Pour ajouter plus de compte:

"account#": { "apiKey":"", "secret":"", "subAccountName":"" }

© 2022 GitHub, Inc.
Terms
Privacy
Security
Status
