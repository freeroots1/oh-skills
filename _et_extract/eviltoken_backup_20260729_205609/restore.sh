#!/bin/bash
echo "🔄 Restoring EvilToken..."
pkill -9 -f gunicorn
cp app.py /root/eviltoken/
cp tokens.db /root/eviltoken/
cp -r templates/* /root/eviltoken/templates/
cp -r static/* /root/eviltoken/static/ 2>/dev/null
cd /root/eviltoken
nohup gunicorn -w 1 -b 0.0.0.0:5000 --timeout 300 app:app > /tmp/gunicorn.log 2>&1 &
sleep 3
echo "✅ Restore complete!"
