import { Component, Input } from '@angular/core';
import { CustomInputComponent } from '../../components/shared/custom-input/custom-input.component'
import { TopicsCarouselComponent } from '../../components/topics-carousel/topics-carousel.component'
import { HintTooltipComponent } from '../../components/shared/hint-tooltip/hint-tooltip.component'
import { Router, ActivatedRoute } from '@angular/router';
import { TopicDataModel } from '../../utils/models'

@Component({
  selector: 'topic-landing-layout',
  standalone: true,
  imports: [
    CustomInputComponent,
    TopicsCarouselComponent,
    HintTooltipComponent
  ],
  templateUrl: './topic-landing-layout.component.html',
})

export class TopicLandingLayoutComponent {

  @Input() titleTxt: string = ''
  @Input() projectId: string = ''
  @Input() topicList!: TopicDataModel[]

  searchTerm: string = ''

  constructor(
    private router: Router,
    private route: ActivatedRoute,
  ){}

  handleSearch = (searchTerm: string) => {
    this.searchTerm = searchTerm

  }

  handleExploreClick = (e: Event) => {    
    this.router.navigate(['comparison'], { 
      relativeTo: this.route,
      queryParams: { 
        searchTerm:  this.searchTerm,
        area: this.projectId
      }
    });
  }
}
