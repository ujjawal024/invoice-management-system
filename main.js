function addItem() {
    const table = document.getElementById("invoiceBody");
    const row = table.insertRow();
  
    row.innerHTML = `
      <td><input type="text" placeholder="Item Name" /></td>
      <td><input type="number" value="1" min="1" oninput="calculateTotal()" /></td>
      <td><input type="number" value="0" min="0" oninput="calculateTotal()" /></td>
      <td>₹ 0</td>
      <td><button class="btn btn-danger" onclick="removeItem(this)">Remove</button></td>
    `;
  
    calculateTotal();
  }
  
  function removeItem(button) {
    button.closest("tr").remove();
    calculateTotal();
  }
  
  function calculateTotal() {
    const rows = document.querySelectorAll("#invoiceBody tr");
    let totalAmount = 0;
  
    rows.forEach(row => {
      const qty = parseFloat(row.cells[1].querySelector("input").value) || 0;
      const price = parseFloat(row.cells[2].querySelector("input").value) || 0;
      const total = qty * price;
      row.cells[3].innerText = `₹ ${total.toFixed(2)}`;
      totalAmount += total;
    });
  
    document.getElementById("totalAmount").innerText = totalAmount.toFixed(2);
  }
  
  async function saveCustomer() {
    const name = document.getElementById("customerName").value;
    const customerData = {
      name: name,
      email: "sample@email.com",
      phone: "1234567890",
      address: "Some Address"
    };
  
    const res = await fetch("http://127.0.0.1:5000/customers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(customerData)
    });
  
    const data = await res.json();
    return data.customer_id;
  }
  
  async function submitInvoice() {
    const customerId = await saveCustomer();
    const rows = document.querySelectorAll("#invoiceBody tr");
  
    const items = Array.from(rows).map(row => {
      return {
        product_id: 1,
        quantity: parseFloat(row.cells[1].querySelector("input").value),
        unit_price: parseFloat(row.cells[2].querySelector("input").value)
      };
    });
  
    const invoiceData = {
      customer_id: customerId,
      items: items
    };
  
    const res = await fetch("http://127.0.0.1:5000/invoices", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(invoiceData)
    });
  
    const result = await res.json();
    alert("Invoice saved! ID: " + result.invoice_id);
  }
  
  async function loadAllInvoices() {
    const res = await fetch("http://127.0.0.1:5000/invoices");
    const invoices = await res.json();
  
    let html = "<h3>Invoice History</h3><ul>";
    invoices.forEach(inv => {
      html += `
        <li>
          ID: ${inv.invoice_id}, Customer: ${inv.customer_name}, Date: ${inv.invoice_date}, Total: ₹${inv.total_amount}
          <button onclick="deleteInvoice(${inv.invoice_id})">🗑️ Delete</button>
        </li>
      `;
    });
    html += "</ul>";
  
    document.getElementById("invoiceList").innerHTML = html;
  }
  
  async function deleteInvoice(id) {
    const res = await fetch(`http://127.0.0.1:5000/invoices/${id}`, { method: "DELETE" });
    const result = await res.json();
    alert(result.message);
    loadAllInvoices();
  }
  
  function printInvoice() {
    const customerName = document.getElementById("customerName").value;
    const rows = document.querySelectorAll("#invoiceBody tr");
    let printableContent = `
      <html>
      <head>
        <title>Invoice</title>
        <style>
          body { font-family: Arial; padding: 20px; }
          h2, h3 { margin-bottom: 10px; }
          table { width: 100%; border-collapse: collapse; margin-top: 20px; }
          th, td { border: 1px solid #333; padding: 8px; text-align: left; }
          th { background-color: #f2f2f2; }
          .total { text-align: right; font-weight: bold; margin-top: 20px; }
        </style>
      </head>
      <body>
        <h2>Invoice</h2>
        <p><strong>Customer:</strong> ${customerName}</p>
        <table>
          <thead>
            <tr>
              <th>Item</th>
              <th>Qty</th>
              <th>Price</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>`;
  
    let totalAmount = 0;
  
    rows.forEach(row => {
      const item = row.cells[0].querySelector("input").value;
      const qty = parseFloat(row.cells[1].querySelector("input").value);
      const price = parseFloat(row.cells[2].querySelector("input").value);
      const total = qty * price;
      totalAmount += total;
  
      printableContent += `
        <tr>
          <td>${item}</td>
          <td>${qty}</td>
          <td>₹${price.toFixed(2)}</td>
          <td>₹${total.toFixed(2)}</td>
        </tr>`;
    });
  
    printableContent += `
          </tbody>
        </table>
        <p class="total">Total Amount: ₹${totalAmount.toFixed(2)}</p>
      </body>
      </html>
    `;
  
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printableContent);
    printWindow.document.close();
    printWindow.print();
  }
  