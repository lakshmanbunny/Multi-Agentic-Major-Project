import React from 'react';

const ResearchFeed = ({ data }) => {
    // 1. Debugging: Print received data to console
    console.log("🔍 ResearchFeed Received Data:", data);

    // 2. Safe Destructuring with defaults
    const {
        queries = [],
        dataset_name = '',
        dataset_url = '',
        source_type = '',
        papers = []
    } = data || {};

    // 3. Check if we actually have data
    const hasQueries = queries.length > 0;
    const hasDataset = !!dataset_url;
    const hasPapers = papers.length > 0;
    const isEmpty = !hasQueries && !hasDataset && !hasPapers;

    console.log("📊 Data Status:", { hasQueries, hasDataset, hasPapers, isEmpty });

    if (isEmpty) {
        return (
            <div className="flex flex-col items-center justify-center h-64 text-gray-500 p-6 border border-dashed border-gray-700 rounded-lg">
                <span className="material-symbols-outlined text-6xl mb-4 opacity-50">search_off</span>
                <p className="text-lg font-medium">No research data available yet</p>
                <p className="text-xs mt-2 text-gray-600">Agent is searching...</p>

                {/* DEBUG DATA DUMP */}
                <details className="mt-4 text-left w-full">
                    <summary className="text-xs cursor-pointer text-blue-400 hover:text-blue-300 font-mono">
                        🐛 View Raw Debug Data (Click to expand)
                    </summary>
                    <pre className="text-[10px] bg-black/50 p-3 mt-2 rounded overflow-auto max-h-64 border border-gray-800 font-mono">
                        {JSON.stringify(data, null, 2)}
                    </pre>
                </details>
            </div>
        );
    }

    return (
        <div className="h-full overflow-y-auto p-4 space-y-6 custom-scrollbar">

            {/* DEBUG PANEL - Always visible during development */}
            <details className="bg-yellow-900/10 border border-yellow-800/30 rounded p-2">
                <summary className="text-[10px] cursor-pointer text-yellow-400 font-mono">
                    🐛 Debug Info (queries: {queries.length}, dataset: {hasDataset ? 'YES' : 'NO'}, papers: {papers.length})
                </summary>
                <pre className="text-[9px] bg-black/30 p-2 mt-1 rounded overflow-auto max-h-32 font-mono text-gray-400">
                    {JSON.stringify({ queries, dataset_name, dataset_url, source_type, papers }, null, 2)}
                </pre>
            </details>

            {/* SECTION 1: SEARCH STRATEGY */}
            {hasQueries && (
                <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden font-mono text-sm">
                    <div className="bg-gray-800 px-4 py-2 flex items-center gap-2 border-b border-gray-700">
                        <span className="material-symbols-outlined text-cyan-400 text-sm">terminal</span>
                        <span className="text-gray-300 font-semibold">Search Strategy</span>
                    </div>
                    <div className="p-4 space-y-2 text-green-400">
                        {queries.map((q, idx) => (
                            <div key={idx} className="flex gap-2">
                                <span className="text-cyan-400 select-none">$</span>
                                <span>{q}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* SECTION 2: DATASET IDENTITY */}
            {hasDataset && (
                <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl border border-gray-700 p-1 shadow-lg group hover:border-cyan-500/30 transition-all">
                    <div className="bg-gray-900/50 backdrop-blur p-4 rounded-lg">
                        <div className="flex justify-between items-start mb-3">
                            <div className="p-2 bg-blue-500/10 rounded-lg ring-1 ring-blue-500/30">
                                <span className="material-symbols-outlined text-blue-400 text-2xl">
                                    {source_type === 'kaggle' ? 'cloud_download' : 'folder_data'}
                                </span>
                            </div>
                            {source_type === 'kaggle' && (
                                <span className="px-2 py-1 bg-cyan-900/30 text-cyan-300 text-xs font-bold rounded border border-cyan-800 font-mono">
                                    KAGGLE
                                </span>
                            )}
                        </div>
                        <h3 className="text-white font-bold text-lg mb-1 truncate" title={dataset_name}>
                            {dataset_name || 'Unknown Dataset'}
                        </h3>
                        <div className="flex items-center gap-2 text-xs text-gray-400 mb-4">
                            <span className="truncate break-all">{dataset_url}</span>
                        </div>
                        <a
                            href={dataset_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center justify-center gap-2 w-full py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded transition-colors"
                        >
                            <span className="material-symbols-outlined text-sm">open_in_new</span>
                            View Source
                        </a>
                    </div>
                </div>
            )}

            {/* SECTION 3: LITERATURE REVIEW */}
            {hasPapers && (
                <div>
                    <h3 className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-3 flex items-center gap-2">
                        <span className="material-symbols-outlined text-sm">menu_book</span>
                        Literature Review
                    </h3>
                    <div className="space-y-3">
                        {papers.map((paper, idx) => (
                            <a
                                key={idx}
                                href={paper.url || '#'}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block bg-gray-800/50 hover:bg-gray-800 border border-gray-700 hover:border-cyan-500/50 p-4 rounded-lg transition-all group"
                            >
                                <div className="flex justify-between items-start gap-4">
                                    <h4 className="text-gray-200 font-medium text-sm group-hover:text-cyan-400 transition-colors line-clamp-2">
                                        {paper.title || 'Untitled Paper'}
                                    </h4>
                                    <div className="flex items-center gap-1 shrink-0">
                                        {paper.url && paper.url.toLowerCase().endsWith('.pdf') && (
                                            <span className="material-symbols-outlined text-red-400 text-xs" title="PDF Document">
                                                picture_as_pdf
                                            </span>
                                        )}
                                        <span className="material-symbols-outlined text-gray-600 group-hover:text-gray-400 text-xs">
                                            open_in_new
                                        </span>
                                    </div>
                                </div>
                                {paper.summary && (
                                    <p className="text-gray-500 text-xs mt-2 line-clamp-3">
                                        {paper.summary}
                                    </p>
                                )}
                                <div className="mt-2 flex gap-2">
                                    <span className="text-[10px] bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded uppercase font-mono">
                                        {paper.source || 'Web'}
                                    </span>
                                </div>
                            </a>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ResearchFeed;
