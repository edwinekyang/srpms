import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractViewerComponent } from './contract-viewer.component';
import {HttpClient} from '@angular/common/http';
import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';

describe('ContractViewerComponent', () => {
  let component: ContractViewerComponent;
  let fixture: ComponentFixture<ContractViewerComponent>;
  let httpClient: HttpClient;
  let httpTestingController: HttpTestingController;
  let message: any;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      declarations: [ ContractViewerComponent ]
    })
    .compileComponents();

    // Inject the http service and test controller for each test
    httpClient = TestBed.get(HttpClient);
    httpTestingController = TestBed.get(HttpTestingController);
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ContractViewerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  // it('should create', () => {
  //   expect(component).toBeTruthy();
  // });
});
