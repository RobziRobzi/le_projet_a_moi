# le_projet_a_moi
Surveillance et Régulation de la Tension Électrique ⚡
📌 Description du projet

Ce projet a pour objectif de surveiller la tension sur une ligne électrique à l’aide d’un capteur, puis de contrôler deux actionneurs (disjoncteurs) :

Si la tension est trop haute, le premier disjoncteur est activé.

Si la tension est trop basse, le second disjoncteur est activé.

Ce système permet de réguler automatiquement la tension et d’assurer une meilleure protection de l’installation.


🔧 Fonctionnement

Le capteur mesure la tension en temps réel.

Le programme compare la tension mesurée avec des seuils de sécurité (tension minimale et maximale).

En fonction de la valeur mesurée :

Si tension > seuil_max → activation du disjoncteur haute tension.

Si tension < seuil_min → activation du disjoncteur basse tension.

Sinon → aucun disjoncteur n’est activé.