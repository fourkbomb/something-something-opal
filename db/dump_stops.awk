BEGIN {
	FS="\",\""
}

/[0-9]/ {
	sub(/"/, "", $1)
	sub(/"/, "", $9)
	sub(/'/, "''", $3)
	print "INSERT INTO stops VALUES ('" $1 "', '" $3 "', " $4 "," $5 ", '" $7 "', " $8 ", '" $9 "');\n"
}

