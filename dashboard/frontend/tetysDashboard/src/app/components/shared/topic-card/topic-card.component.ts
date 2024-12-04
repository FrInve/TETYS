import { Component, Input , Output, EventEmitter, OnChanges, SimpleChanges} from '@angular/core';
import { CommonModule } from '@angular/common';
import { WordCloudComponent } from '../../shared/word-cloud/word-cloud.component';
import { TopicDataModel } from '../../../utils/models'
import { Router } from '@angular/router';

@Component({
  selector: 'topic-card',
  standalone: true,
  imports: [
    CommonModule,
    WordCloudComponent
  ],
  templateUrl: './topic-card.component.html',
})
export class TopicCardComponent implements OnChanges {

  @Input() wordCloudId: string = ''
  @Input() topicObj!: TopicDataModel
  @Input() extraQuery?: {
    key: string,
    value: string
  }
  @Input() hasSimilarityScore?: boolean = false

  @Input() selectable: boolean = false
  @Input() disabledSelect: boolean = false
  @Input() selectedIds: Set<number> = new Set()
  @Output() checkboxClick: EventEmitter<any> = new EventEmitter<any>();

  wordCloudData: {
    word: string, 
    frequency: number
  }[] = []

  constructor(private router: Router) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes["topicObj"]?.currentValue.id !== changes["topicObj"]?.previousValue?.id) {
      this.topicObj.terms.forEach((term) => {
        this.wordCloudData.push({
          word: term[0], 
          frequency: term[1]
        })
      })
    }
  }

  navigateToTopicDetail = () => {
    const urlSegments = this.router.url.split('/');
    let area = urlSegments[1];
  
    // Create the base query params object
    let queryParams: any = { area: area };
  
    if (this.hasSimilarityScore) {
      queryParams.similarityScore = Math.round(100*this.topicObj.relevance!);
    }

    if (this.extraQuery) {
      queryParams[this.extraQuery.key] = this.extraQuery.value
    }
  
    // Construct the URL with the query parameters
    const urlTree = this.router.createUrlTree(
      ['/tetys/topic', this.topicObj.id],
      { queryParams: queryParams }
    );
    const fullUrl = this.router.serializeUrl(urlTree);

    // Open the constructed URL in a new tab
    window.open(fullUrl, '_blank');
  }
}
