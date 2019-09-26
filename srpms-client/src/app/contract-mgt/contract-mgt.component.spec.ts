import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractMgtComponent } from './contract-mgt.component';
import {MatCardModule, MatListModule} from '@angular/material';
import {HttpClient} from '@angular/common/http';
import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';

describe('ContractMgtComponent', () => {
  let component: ContractMgtComponent;
  let fixture: ComponentFixture<ContractMgtComponent>;
  let httpClient: HttpClient;
  let httpTestingController: HttpTestingController;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ContractMgtComponent ],
      imports: [MatListModule, MatCardModule, HttpClientTestingModule],
    })
    .compileComponents();

    // Inject the http service and test controller for each test
    httpClient = TestBed.get(HttpClient);
    httpTestingController = TestBed.get(HttpTestingController);
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ContractMgtComponent);
    component = fixture.componentInstance;
    component.accountService.login({});
    fixture.detectChanges();
  });
  //
  // it('should create', () => {
  //   expect(component).toBeTruthy();
  // });
});
