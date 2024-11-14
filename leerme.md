
#Crea y pobla la bd, primero se crea el usuario con los accesos y la bd en el pgadmin con las tablas

#Esto reinicia toda la BD igual

python odoo-bin -r odoo -w odoo --addons-path=addons -d odoo -i base

#Con esto ejecutas ODOO ya no es necesario el -i base porque ya ejecutaste el comando anterior 

python odoo-bin -r odoo -w odoo --addons-path=addons -d odoo 


#Modulos a instalar
- Account

lo instalan desde la interfaz de Odoo, si lo hacen desde el manifest lo hace mal, lo instalan antes de importar el modulo de gestion educativa

#Cuando desarrolles modulos propios
python odoo-bin -r odoo -w odoo --addons-path=addons,modules -d odoo 



#user=admin password=admin, esto lo crea odoo


#Digital Ocean
123456OdooRoot



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


#Para seguir los logs
docker logs -f odoo_web_1

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
https://github.com/GuidoSV7/odooingsw1