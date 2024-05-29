## With vscode you can do this

code --diff docs/database-design.json docs/database_design-new.json

## To merge files you can use this command or just commit it and see the differences and then do a second commit to merge them manualy

diff --line-format %L database_design.json database_design-new.json > newfile.json
