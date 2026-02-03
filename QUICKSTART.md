# 🚀 Quick Start Guide - Local Notebook

## What You Have Now

✅ **miniLM.ipynb** - Complete RAG system with LLM integration  
✅ **Full conversational answers** - Not just documents!  
✅ **Intelligent routing** - Automatically picks the right document type  
✅ **Your documents** - iPhone 17 PDF, F1 DOCX, Sales CSV

---

## How to Run (3 Steps)

### Step 1: Make Sure Your API Key is Set

Check your `.env` file has your real OpenRouter API key:
```
OPENROUTER_API_KEY=your_actual_key_here
```

If you don't have one:
1. Go to https://openrouter.ai/
2. Sign up and get your API key
3. Add some credits ($5 minimum recommended)

### Step 2: Open the Notebook

```bash
jupyter notebook miniLM.ipynb
```

Or use VS Code / Jupyter Lab if you prefer.

### Step 3: Run All Cells

In Jupyter:
1. Click **"Cell"** → **"Run All"**
2. Wait ~1-2 minutes for initial setup
3. Scroll to the bottom and use the query examples!

---

## What Happens When You Run

### Initial Setup (First Time Only)
```
Step 1: ✅ Environment variables loaded
Step 2: ✅ All libraries imported
Step 3: ✅ Embedding model loaded (768 dimensions)
Step 4: ✅ LLM initialized (OpenRouter)
Step 5: ✅ Documents loaded (PDF: 6 pages, DOCX: 1 doc, CSV: 9994 rows)
Step 6: ✅ Vector stores created
Step 7: ✅ QA chains created
Step 8: ✅ Router configured
Step 9: ✅ SYSTEM READY!
```

### Now You Can Ask Questions!

The notebook includes example cells for:

**CSV Queries:**
```python
query_documents("Can you list me five corporate segment orders?")
```

**PDF Queries:**
```python
query_documents("What are the main features of iPhone 17?")
```

**DOCX Queries:**
```python
query_documents("Who won the Singapore Grand Prix 2025?")
```

---

## What You Get Back

### With LLM (What You Have Now) ✅

**Your Question:** "Can you list me five corporate segment orders?"

**LLM Answer:**
```
Here are five corporate segment orders from the sales data:

1. Order US-2017-124303 - Fred Hopkins purchased Wirebound 
   Message Books for $16.06
2. Order CA-2017-132976 - Andrew Gjertsen bought Post-it 
   Note Pads for $11.65
3. Order US-2017-145366 - Christine Abelman ordered 
   Recycled Envelopes for $57.58
4. Order US-2014-100853 - Jennifer Braxton purchased a 
   Power Control Center for $52.45
5. Order US-2014-156216 - Erin Ashbrook bought an Index 
   System for $18.65

All of these orders belong to the Corporate customer segment.
```

**That's a natural, conversational answer!** ✨

---

## Customizing Your Queries

At the bottom of the notebook, there's a cell for your own questions:

```python
# Ask your own question here
my_question = "What is the total sales for corporate segment?"

query_documents(my_question)
```

Just edit `my_question` and run the cell!

---

## How the Router Works

The system **automatically** determines which document type to search:

- **Question about orders/sales** → Routes to **CSV**
- **Question about iPhone** → Routes to **PDF**  
- **Question about F1/race** → Routes to **DOCX**

You don't need to specify document type - it's smart!

---

## Troubleshooting

### Error: "User not found" (401)
- Your OpenRouter API key needs credits
- Go to https://openrouter.ai/settings/credits
- Add $5 (will last a long time with free model)

### Error: "Module not found"
```bash
pip install -r requirements.txt
```

### Notebook not opening
```bash
pip install jupyter ipykernel
```

### Results not conversational (just showing documents)
- Make sure you're running the `miniLM.ipynb` notebook
- Check that the LLM is initialized (Step 4 should show "✅ LLM initialized")

---

## File Structure

```
Document-Search-Engine/
├── miniLM.ipynb          # ⭐ Main notebook - RUN THIS
├── requirements.txt      # Dependencies
├── .env                  # Your API key (DO NOT SHARE)
├── .env.example          # Template for API key
├── README.md            # Project documentation
├── QUICKSTART.md        # This file
├── iphone17.pdf         # Sample PDF
├── f1info.docx          # Sample DOCX
└── sales.csv            # Sample CSV
```

---

## Next Steps

1. ✅ Run `miniLM.ipynb` 
2. ✅ Try the example queries
3. ✅ Ask your own questions
4. 📝 Check README.md for more details
5. 🚀 Add your own documents (just drop PDF/DOCX/CSV files in the folder)

---

## Tips

- First run takes 1-2 minutes (loads models)
- Subsequent runs are much faster (uses cache)
- You can ask questions in natural language
- The more specific your question, the better the answer
- All processing is local except LLM API calls

---

## Need Help?

Check the notebook cells - they have detailed comments and explanations!

---

**You're all set! Open `miniLM.ipynb` and start asking questions!** 🎉
