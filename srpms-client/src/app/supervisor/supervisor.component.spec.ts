import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SupervisorComponent } from './supervisor.component';
import {MatCardModule, MatListModule} from '@angular/material';
import {HttpClient} from '@angular/common/http';
import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';

describe('SupervisorComponent', () => {
  let component: SupervisorComponent;
  let fixture: ComponentFixture<SupervisorComponent>;
  let httpClient: HttpClient;
  let httpTestingController: HttpTestingController;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SupervisorComponent ],
      imports: [MatListModule, MatCardModule, HttpClientTestingModule],
    })
    .compileComponents();

    // Inject the http service and test controller for each test
    httpClient = TestBed.get(HttpClient);
    httpTestingController = TestBed.get(HttpTestingController);
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SupervisorComponent);
    component = fixture.componentInstance;
    component.accountService.login({});
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
