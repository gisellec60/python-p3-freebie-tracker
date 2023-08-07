from sqlalchemy import ForeignKey, Column, Integer, String, MetaData
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc

engine = create_engine('sqlite:///freebies.db')
Session = sessionmaker(bind=engine)
session = Session()

convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}
metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer(), primary_key=True)
    name = Column(String())
    founding_year = Column(Integer())

    freebies = relationship('Freebie', backref=backref('company'))

    devs = association_proxy('freebies', 'dev',
           creator=lambda dev: Freebie(dev))
    
    def give_freebie(self, dev, item_name, value):
            new_freebie = Freebie(item_name=item_name, value=value)
            new_freebie.company = self
            new_freebie.dev = dev 
            print (f'{new_freebie.dev} {new_freebie.item_name} {new_freebie.value} {new_freebie.company}')
    
    @classmethod      
    def oldest_company(cls):
        oldest_company = session.query(Company.name).order_by(desc(
                Company.founding_year)).first()
        return oldest_company
        
    def __repr__(self):
        return f'<Company {self.name}>'

class Dev(Base):
    __tablename__ = 'devs'

    id = Column(Integer(), primary_key=True)
    name= Column(String())

    freebies = relationship('Freebie', backref=backref('dev'))
    companies = association_proxy('freebies', 'company',
           creator=lambda comp: Freebie(company=comp))
    
    def received_one(self, item_name):
        print(item_name)
        print(self.freebies)
        if item_name in self.freebies:
            return True
        return False     
    
    def give_away(self, dev,freebie):
        if freebie in self.freebies:
            freebie.dev = dev
            session.commit()
        return freebie.dev    
            
    def __repr__(self):
        return f'<Dev {self.name}>'

class Freebie(Base):
    __tablename__ = 'freebies'

    id = Column(Integer(), primary_key=True)

    item_name = Column(String())
    value = Column(Integer())

    dev_id = Column(Integer(), ForeignKey('devs.id'))
    company_id = Column(Integer(), ForeignKey('companies.id')) 
    
    def __repr__(self):
        return f'{self.item_name}'
    
    def print_details(self):
        freebies = session.query(Freebie).all()
        for freebie in freebies:
            print (f'{freebie.dev} owns a {freebie.item_name} from {freebie.company}')