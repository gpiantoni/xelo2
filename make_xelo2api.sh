mkdir tmp
cat > tmp/xelo2api.py <<EOF
DATABASE_NAME = 'testdb'
USERNAME = 'giovanni'
PASSWORD = ''

EOF

grep '>>>' docs/tutorials/xelo2api.md >> tmp/xelo2api.py
sed -i 's/>>> //' tmp/xelo2api.py

