import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractViewerComponent } from './contract-viewer.component';
import {HttpClient} from '@angular/common/http';
import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';
import {MatCardModule, MatDialogModule, MatDividerModule, MatFormFieldModule, MatRadioModule, MatSelectModule} from '@angular/material';
import {ReactiveFormsModule} from '@angular/forms';
import {ActivatedRoute} from '@angular/router';
import {RouterTestingModule} from '@angular/router/testing';

describe('ContractViewerComponent', () => {
  let component: ContractViewerComponent;
  let fixture: ComponentFixture<ContractViewerComponent>;
  let httpClient: HttpClient;
  let httpTestingController: HttpTestingController;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
          HttpClientTestingModule,
          MatDividerModule,
          MatFormFieldModule,
          MatSelectModule,
          MatRadioModule,
          MatCardModule,
          ReactiveFormsModule,
          MatDialogModule,
          RouterTestingModule,
      ],
      declarations: [ ContractViewerComponent ],
      providers: [
          { provide: ActivatedRoute,
            useValue: {
              paramMap: {contractId: 1}
            }
          },
      ],
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
/*
  it('should create', () => {
    expect(component).toBeTruthy();
  });*/
});
