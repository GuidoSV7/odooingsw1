
#Crea y pobla la bd, primero se crea el usuario con los accesos y la bd en el pgadmin con las tablas

#Esto reinicia toda la BD igual

python odoo-bin -r odoo -w odoo --addons-path=addons -d odoo -i base

#Con esto ejecutas ODOO ya no es necesario el -i base porque ya ejecutaste el comando anterior 

python odoo-bin -r odoo -w odoo --addons-path=addons -d odoo 


#user=admin password=admin, esto lo crea odoo
