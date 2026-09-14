require('dotenv').config();

const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

// Add or remove test advisors here
const advisors = [
  {
    name: 'Ana Martins',
    description: 'Machine learning and artificial intelligence for healthcare.',
    university: 'Universidade de São Paulo',
    department: 'Epidemiology',
    email: 'ana.martins@example.edu',
    profile_url: 'https://example.edu/ana-martins',
    keywords: ['machine learning', 'healthcare', 'AI']
  },
  {
    name: 'Bruno Almeida',
    description: 'Natural language processing and large language models.',
    university: 'Universidade Federal de Minas Gerais',
    department: 'Computer Science',
    email: 'bruno.almeida@example.edu',
    profile_url: 'https://example.edu/bruno-almeida',
    keywords: ['NLP', 'large language models', 'generative AI']
  },
  {
    name: 'Carolina Ferreira',
    description: 'Causal inference and statistical methods for health research.',
    university: 'Universidade Federal do Rio de Janeiro',
    department: 'Statistics',
    email: 'carolina.ferreira@example.edu',
    profile_url: 'https://example.edu/carolina-ferreira',
    keywords: ['causal inference', 'statistics', 'health policy']
  },
  {
    name: 'Daniel Costa',
    description: 'Fairness, interpretability, and responsible machine learning.',
    university: 'Universidade Estadual de Campinas',
    department: 'Computer Science',
    email: 'daniel.costa@example.edu',
    profile_url: 'https://example.edu/daniel-costa',
    keywords: ['fairness', 'interpretability', 'responsible AI']
  },
  {
    name: 'Elena Rodrigues',
    description: 'Bioinformatics and machine learning for genomic data.',
    university: 'Universidade Federal do Rio Grande do Sul',
    department: 'Molecular Biology',
    email: 'elena.rodrigues@example.edu',
    profile_url: 'https://example.edu/elena-rodrigues',
    keywords: ['bioinformatics', 'genomics', 'machine learning']
  }
];

async function seed() {
  console.log(`Inserting ${advisors.length} advisors...`);

  const { data, error } = await supabase
    .from('advisors')
    .insert(advisors)
    .select();

  if (error) {
    console.error('Seed failed:', error.message);
    process.exit(1);
  }

  console.log(`Successfully inserted ${data.length} advisors.`);
}

seed();
