require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { createClient } = require('@supabase/supabase-js');

const app = express();

app.use(cors());
app.use(express.json());

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);


// Get all advisors
app.get('/advisors', async (req, res) => {
  const { data, error } = await supabase
    .from('advisors')
    .select('*');

  if (error) {
    return res.status(500).json({
      error: error.message
    });
  }

  res.json(data);
});


// Search advisors
app.get('/advisors/search', async (req, res) => {
  const query = req.query.q?.trim();

  if (!query) {
    return res.status(400).json({
      error: 'Missing search query'
    });
  }

  const { data, error } = await supabase
    .rpc('search_advisors', {
      search_query: query
    });

  if (error) {
    console.error('Search error:', error);

    return res.status(500).json({
      error: error.message
    });
  }

  res.json(data);
});


// Start server
app.listen(3000, () => {
  console.log('CMOrienta API running at http://localhost:3000');
});

