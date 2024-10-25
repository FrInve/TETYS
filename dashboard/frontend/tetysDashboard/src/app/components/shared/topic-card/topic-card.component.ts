import { Component, Input , Output, EventEmitter, OnChanges, SimpleChanges} from '@angular/core';
import { CommonModule } from '@angular/common';
import { WordCloudComponent } from '../../shared/word-cloud/word-cloud.component';
import { TopicDataModel } from '../../../utils/models'

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
  @Input() hasSimilarityScore?: boolean = false

  @Input() selectable: boolean = false
  @Input() disabledSelect: boolean = false
  @Input() selectedIds: Set<string> = new Set()
  @Output() checkboxClick: EventEmitter<any> = new EventEmitter<any>();

  wordCloudData: {
    word: string, 
    frequency: number
  }[] = []

  ngOnChanges(changes: SimpleChanges): void {
    if (changes["topicObj"].currentValue.id !== changes["topicObj"].previousValue?.id) {
      this.topicObj.terms.forEach((term) => {
        this.wordCloudData.push({
          word: term[0], 
          frequency: term[1]
        })
      })
    }
  }
}
