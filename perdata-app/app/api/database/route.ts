import { NextRequest, NextResponse } from 'next/server';
import corpusData from '../../../data/corpus.json';

interface ArticleItem {
  pasal: string;
  source: string;
  buku?: string;
  bab?: string;
  bagian?: string;
  bab_title?: string;
  content: string;
  sha256?: string;
}

const articles: ArticleItem[] = corpusData as ArticleItem[];

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const q = searchParams.get('q')?.trim().toLowerCase() || '';
    const source = searchParams.get('source')?.trim().toLowerCase() || '';
    const category = searchParams.get('category')?.trim().toLowerCase() || '';
    const limit = Math.min(100, Math.max(1, parseInt(searchParams.get('limit') || '12', 10)));
    const offset = Math.max(0, parseInt(searchParams.get('offset') || '0', 10));

    let filtered = articles;

    // Filter source (KUHPerdata / HIR)
    if (source) {
      filtered = filtered.filter((c) => c.source.toLowerCase() === source);
    }

    // Filter category (Buku / Bab / Bagian)
    if (category) {
      if (category.includes(':')) {
        const [bukuPart, babPart] = category.split(':').map((s) => s.trim());
        filtered = filtered.filter(
          (c) =>
            (c.buku || '').toLowerCase().includes(bukuPart) &&
            ((c.bab || '').toLowerCase().trim() === babPart ||
              (c.bagian || '').toLowerCase().trim() === babPart ||
              (c.bagian || '').toLowerCase().includes(babPart))
        );
      } else {
        filtered = filtered.filter(
          (c) =>
            (c.buku || '').toLowerCase().includes(category) ||
            (c.bagian || '').toLowerCase().includes(category) ||
            (c.bab || '').toLowerCase().trim() === category ||
            (c.bab || '').toLowerCase().includes(category)
        );
      }
    }

    // Filter query text atau nomor pasal
    if (q) {
      filtered = filtered.filter(
        (c) =>
          c.pasal.toLowerCase() === q ||
          c.pasal.toLowerCase().includes(q) ||
          c.content.toLowerCase().includes(q) ||
          (c.buku || '').toLowerCase().includes(q) ||
          (c.bab || '').toLowerCase().includes(q) ||
          (c.bagian || '').toLowerCase().includes(q)
      );
    }

    const total = filtered.length;
    const paged = filtered.slice(offset, offset + limit);

    return NextResponse.json({
      total,
      offset,
      limit,
      articles: paged,
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: 'Gagal memuat database pasal', details: error?.message },
      { status: 500 }
    );
  }
}
