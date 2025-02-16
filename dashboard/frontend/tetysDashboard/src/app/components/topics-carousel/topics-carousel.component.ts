import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { WordCloudComponent } from '../shared/word-cloud/word-cloud.component';
import { TopicCardComponent } from '../shared/topic-card/topic-card.component';

@Component({
  selector: 'topics-carousel ',
  standalone: true,
  imports: [
    CommonModule,
    WordCloudComponent,
    TopicCardComponent
  ],
  templateUrl: './topics-carousel.component.html',
})

export class TopicsCarouselComponent implements OnInit, OnDestroy {
  @Input() data: any[] = []
  @Input() visibleCards: number = 3

  currentIndex = 0;
  intervalId: any;

  constructor(
    public router: Router
  ) {}

  ngOnInit() {
    // Start the automatic sliding when the component is initialized
    this.startAutoSlide();
  }

  ngOnDestroy() {
    // Clear the interval when the component is destroyed to prevent memory leaks
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }

  get carouselStyle() {
    let offset = (this.currentIndex) * -100;
    return {
      transform: `translateX(calc(${offset}% - ${this.currentIndex}rem))`,
      transition: 'transform 0.3s ease-in-out',
      width: `${95/this.visibleCards}%`
    };
  }

  startAutoSlide() {
    this.intervalId = setInterval(() => {
      this.next();
    }, 9000); // Slide every 3 seconds
  }

  next() {
    this.currentIndex = this.currentIndex + 1
    if(this.currentIndex > this.data.length - this.visibleCards) {
      this.currentIndex = 0
    }
  }

  prev() {
    this.currentIndex = this.currentIndex - 1
    if(this.currentIndex < 0) {
      this.currentIndex = this.data.length - this.visibleCards
    }
  }
}
