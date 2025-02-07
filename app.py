from flask import Flask, render_template, jsonify, request
import re
import os

app = Flask(__name__)

def extract_amount(filename):
    # 使用正则表达式匹配金额
    # 针对高德发票格式：【公司名-金额元-N个行程】
    # 或者直接是数字.pdf格式
    patterns = [
        r'-(\d+(?:\.\d{0,2}))元-',  # 匹配【公司名-金额元-N个行程】格式
        r'^(\d+(?:\.\d{0,2}))\.pdf$'  # 匹配直接数字.pdf格式
    ]
    
    amounts = []
    for pattern in patterns:
        found = re.findall(pattern, filename)
        amounts.extend(found)
    
    # 转换为浮点数
    cleaned_amounts = []
    for amount in amounts:
        try:
            cleaned_amounts.append(float(amount))
        except ValueError:
            continue
    
    return cleaned_amounts

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_files():
    files = request.json.get('files', [])
    
    if not files or len(files) > 100:
        return jsonify({
            'error': '请上传1-100个文件'
        }), 400
        
    total_amount = 0
    amounts = []
    results = []
    
    for filename in files:
        file_amounts = extract_amount(filename)
        if file_amounts:
            for amount in file_amounts:
                amounts.append(amount)
                results.append({
                    'filename': filename,
                    'amount': amount
                })
    
    total_amount = sum(amounts)
    calculation = ' + '.join([str(amount) for amount in amounts])
    
    return jsonify({
        'results': results,
        'calculation': calculation,
        'total': total_amount
    })
