export interface TopicDataModel {
    id: number,
    title: string,
    terms: any[][],
    total_documents: number,
    start_date: string,
    end_date: string,
    frequency: string,
    absolute_frequencies: number[],
    relative_frequencies: number[],
    rankings: number[],
    relevance?: number
}