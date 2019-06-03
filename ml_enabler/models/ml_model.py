from ml_enabler import db
from ml_enabler.models.utils import timestamp, bbox_to_polygon_wkt, ST_GeomFromText
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql
from ml_enabler.models.dtos.ml_model_dto import MLModelDTO, MLModelVersionDTO, PredictionDTO


class Prediction(db.Model):
    """ Predictions from a model at a given time """
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=timestamp, nullable=False)
    model_id = db.Column(db.BigInteger, db.ForeignKey(
                        'ml_models.id', name='fk_models'), nullable=False)
    version_id = db.Column(db.Integer, db.ForeignKey(
                          'ml_model_versions.id', name='ml_model_versions_fk'),
                          nullable=False)
    dockerhub_hash = db.Column(db.String)
    bbox = db.Column(Geometry('POLYGON', srid=4326))
    predictions = db.Column(postgresql.JSONB, nullable=False)

    def create(self, prediction_dto: PredictionDTO):
        """ Creates and saves the current model to the DB """

        self.model_id = prediction_dto.model_id
        self.version_id = prediction_dto.version_id
        self.dockerhub_hash = prediction_dto.dockerhub_hash
        self.bbox = ST_GeomFromText(bbox_to_polygon_wkt(prediction_dto.bbox), 4326)
        self.predictions = prediction_dto.predictions

        db.session.add(self)
        db.session.commit()

    def save(self):
        """ Save changes to db"""
        db.session.commit()

    @staticmethod
    def get_predictions_by_model(model_id: int):
        """
        Gets predictions for a specified ML Model
        :param model_id: ml model ID in scope
        :return: predictions if found otherwise None
        """
        return Prediction.query.filter_by(model_id=model_id)

    def delete(self):
        """ Deletes the current model from the DB """
        db.session.delete(self)
        db.session.commit()


class MLModel(db.Model):
    """ Describes an ML model registered with the service """
    __tablename__ = 'ml_models'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=timestamp, nullable=False)
    name = db.Column(db.String, unique=True)
    source = db.Column(db.String)
    dockerhub_url = db.Column(db.String)
    predictions = db.relationship(Prediction, backref='ml_models',
                                  cascade='all, delete-orphan', lazy='dynamic')

    def create(self, ml_model_dto: MLModelDTO):
        """ Creates and saves the current model to the DB """

        self.name = ml_model_dto.name
        self.source = ml_model_dto.source
        self.dockerhub_url = ml_model_dto.dockerhub_url

        db.session.add(self)
        db.session.commit()
        return self

    def save(self):
        """ Save changes to db"""
        db.session.commit()

    @staticmethod
    def get(model_id: int):
        """
        Gets specified ML Model
        :param model_id: ml model ID in scope
        :return: ML Model if found otherwise None
        """
        return MLModel.query.get(model_id)

    @staticmethod
    def get_all():
        return MLModel.query.all()

    def delete(self):
        """ Deletes the current model from the DB """
        db.session.delete(self)
        db.session.commit()

    def as_dto(self):
        model_dto = MLModelDTO()
        model_dto.model_id = self.id
        model_dto.name = self.name
        model_dto.created = self.created
        model_dto.source = self.source
        model_dto.dockerhub_url = self.dockerhub_url

        return model_dto

    def update(self, updated_ml_model_dto: MLModelDTO):
        """ Updates an ML model """
        self.id = updated_ml_model_dto.model_id
        self.name = updated_ml_model_dto.name
        self.source = updated_ml_model_dto.source
        self.dockerhub_url = updated_ml_model_dto.dockerhub_url

        db.session.commit()


class MLModelVersion(db.Model):
    """ Stores versions of all subscribed ML Models """
    __tablename__ = 'ml_model_versions'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=timestamp, nullable=False)
    model_id = db.Column(db.BigInteger, db.ForeignKey(
        'ml_models.id', name='fk_models_versions'), nullable=False)
    version_major = db.Column(db.Integer, nullable=False)
    version_minor = db.Column(db.Integer, nullable=False)
    version_patch = db.Column(db.Integer, nullable=False)

    def create(self, version_dto: MLModelVersionDTO):
        """  Creates a new version of an ML model """

        self.model_id = version_dto.model_id
        self.version_major = version_dto.version_major
        self.version_minor = version_dto.version_minor
        self.version_patch = version_dto.version_patch

        db.session.add(self)
        db.session.commit()
        return self

    def save(self):
        """ Save changes to the db """
        db.session.commit()

    @staticmethod
    def get_version(model_id: int, version_major: int, version_minor: int, version_patch: int):
        return MLModelVersion.query.filter_by(model_id=model_id, version_major=version_major, version_minor=version_minor, version_patch=version_patch).one()

    def as_dto(self):
        version_dto = MLModelVersionDTO()
        version_dto.version_id = self.id
        version_dto.model_id = self.model_id
        version_dto.created = self.created
        version_dto.version_major = self.version_major
        version_dto.version_minor = self.version_minor
        version_dto.version_patch = self.version_patch

        return version_dto
